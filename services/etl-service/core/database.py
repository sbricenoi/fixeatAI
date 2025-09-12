"""
DatabaseManager - Gestor de conexiones y operaciones de BD para ETL Service
Maneja múltiples bases de datos de forma independiente y eficiente
"""

from __future__ import annotations

import os
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass
import asyncio

# Importar dependencias de BD
try:
    import pymysql
    import pymysql.cursors
except ImportError:
    pymysql = None

from .config import ETLConfig, DatabaseConfig

logger = logging.getLogger("etl-service.database")


@dataclass
class ConnectionPool:
    """Pool de conexiones para una BD específica"""
    config: DatabaseConfig
    connections: List[Any]
    active_connections: int = 0
    max_connections: int = 5


class DatabaseManager:
    """Gestor de múltiples bases de datos para ETL"""
    
    def __init__(self, config: ETLConfig):
        self.config = config
        self.connection_pools: Dict[str, ConnectionPool] = {}
        self.health_status: Dict[str, bool] = {}
        
        logger.info(f"🗄️ DatabaseManager inicializado para {len(config.databases)} bases de datos")
    
    async def test_connections(self) -> Dict[str, bool]:
        """Probar conexiones a todas las BDs configuradas"""
        
        results = {}
        
        for db_name, db_config in self.config.databases.items():
            if not db_config.enabled:
                results[db_name] = False
                continue
                
            try:
                connection = await self._create_connection(db_config)
                if connection:
                    await self._test_single_connection(connection, db_name)
                    self._close_connection(connection)
                    results[db_name] = True
                    self.health_status[db_name] = True
                    logger.info(f"✅ Conexión exitosa a BD '{db_name}'")
                else:
                    results[db_name] = False
                    self.health_status[db_name] = False
                    
            except Exception as e:
                logger.error(f"❌ Error conectando a BD '{db_name}': {e}")
                results[db_name] = False
                self.health_status[db_name] = False
        
        return results
    
    async def _create_connection(self, db_config: DatabaseConfig):
        """Crear conexión a BD específica"""
        
        if not pymysql:
            raise RuntimeError("pymysql no está instalado. Ejecutar: pip install pymysql")
        
        try:
            # Configurar SSL si está habilitado
            ssl_config = None
            if db_config.ssl_enabled:
                ssl_config = {
                    "check_hostname": False,
                    "verify_mode": 0  # ssl.CERT_NONE equivalent
                }
                # Solo agregar CA si está especificado
                if db_config.ssl_ca_path:
                    ssl_config["ca"] = db_config.ssl_ca_path
            
            connection = pymysql.connect(
                host=db_config.host,
                port=db_config.port,
                user=db_config.user,
                password=db_config.password,
                database=db_config.database,
                cursorclass=pymysql.cursors.DictCursor,
                connect_timeout=db_config.connection_timeout,
                read_timeout=db_config.read_timeout,
                ssl=ssl_config,
                autocommit=True
            )
            
            return connection
            
        except Exception as e:
            logger.error(f"❌ Error creando conexión: {e}")
            raise
    
    async def _test_single_connection(self, connection, db_name: str):
        """Probar una conexión específica"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 as test")
                result = cursor.fetchone()
                if result and result.get("test") == 1:
                    logger.debug(f"✅ Test de conexión exitoso para '{db_name}'")
                else:
                    raise RuntimeError("Test query no retornó resultado esperado")
        except Exception as e:
            logger.error(f"❌ Test de conexión falló para '{db_name}': {e}")
            raise
    
    def _close_connection(self, connection):
        """Cerrar conexión de BD"""
        try:
            if connection:
                connection.close()
        except Exception as e:
            logger.warning(f"⚠️ Error cerrando conexión: {e}")
    
    async def introspect_schema(self, database_name: str = "default") -> Dict[str, Any]:
        """Introspeccionar esquema de BD específica"""
        
        db_config = self.config.get_database_config(database_name)
        
        try:
            connection = await self._create_connection(db_config)
            
            schema_info = {
                "database": db_config.database,
                "tables": {},
                "introspection_timestamp": asyncio.get_event_loop().time()
            }
            
            with connection.cursor() as cursor:
                # Obtener lista de tablas
                cursor.execute("""
                    SELECT TABLE_NAME, TABLE_ROWS, TABLE_COMMENT
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_SCHEMA = %s 
                    AND TABLE_TYPE = 'BASE TABLE'
                    ORDER BY TABLE_NAME
                """, [db_config.database])
                
                tables = cursor.fetchall()
                
                for table in tables:
                    table_name = table["TABLE_NAME"]
                    table_info = await self._introspect_table(cursor, db_config.database, table_name)
                    table_info["estimated_rows"] = table.get("TABLE_ROWS", 0)
                    table_info["comment"] = table.get("TABLE_COMMENT", "")
                    schema_info["tables"][table_name] = table_info
            
            self._close_connection(connection)
            
            logger.info(f"✅ Esquema introspectado para '{database_name}': {len(schema_info['tables'])} tablas")
            return schema_info
            
        except Exception as e:
            logger.error(f"❌ Error introspectando esquema de '{database_name}': {e}")
            raise
    
    async def _introspect_table(self, cursor, database: str, table_name: str) -> Dict[str, Any]:
        """Introspeccionar tabla específica"""
        
        table_info = {
            "columns": [],
            "primary_key": [],
            "foreign_keys": [],
            "indexes": []
        }
        
        # Obtener columnas
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT, 
                   CHARACTER_MAXIMUM_LENGTH, COLUMN_COMMENT
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
            ORDER BY ORDINAL_POSITION
        """, [database, table_name])
        
        columns = cursor.fetchall()
        for col in columns:
            table_info["columns"].append({
                "name": col["COLUMN_NAME"],
                "type": col["DATA_TYPE"],
                "nullable": col["IS_NULLABLE"] == "YES",
                "default": col["COLUMN_DEFAULT"],
                "max_length": col["CHARACTER_MAXIMUM_LENGTH"],
                "comment": col["COLUMN_COMMENT"]
            })
        
        # Obtener primary key
        cursor.execute("""
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s 
            AND CONSTRAINT_NAME = 'PRIMARY'
            ORDER BY ORDINAL_POSITION
        """, [database, table_name])
        
        pk_columns = cursor.fetchall()
        table_info["primary_key"] = [col["COLUMN_NAME"] for col in pk_columns]
        
        # Obtener foreign keys
        cursor.execute("""
            SELECT COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s 
            AND REFERENCED_TABLE_NAME IS NOT NULL
        """, [database, table_name])
        
        fk_columns = cursor.fetchall()
        for fk in fk_columns:
            table_info["foreign_keys"].append({
                "column": fk["COLUMN_NAME"],
                "ref_table": fk["REFERENCED_TABLE_NAME"],
                "ref_column": fk["REFERENCED_COLUMN_NAME"]
            })
        
        return table_info
    
    async def extract_table_data(self, database_name: str, table_name: str, 
                                batch_size: int = 1000, where_clause: str = "",
                                limit: Optional[int] = None) -> AsyncGenerator[List[Dict[str, Any]], None]:
        """Extraer datos de tabla con paginación"""
        
        db_config = self.config.get_database_config(database_name)
        
        try:
            connection = await self._create_connection(db_config)
            
            # Construir query base
            base_query = f"SELECT * FROM {table_name}"
            if where_clause:
                base_query += f" WHERE {where_clause}"
            
            # Obtener total de registros
            with connection.cursor() as cursor:
                count_query = f"SELECT COUNT(*) as total FROM {table_name}"
                if where_clause:
                    count_query += f" WHERE {where_clause}"
                
                cursor.execute(count_query)
                total_rows = cursor.fetchone()["total"]
                
                if limit:
                    total_rows = min(total_rows, limit)
                
                logger.info(f"📊 Extrayendo {total_rows} registros de '{table_name}' en lotes de {batch_size}")
                
                # Extraer en lotes
                offset = 0
                extracted_rows = 0
                
                while offset < total_rows:
                    current_batch_size = min(batch_size, total_rows - offset)
                    
                    query = f"{base_query} LIMIT {current_batch_size} OFFSET {offset}"
                    cursor.execute(query)
                    
                    batch = cursor.fetchall()
                    if not batch:
                        break
                    
                    yield batch
                    
                    extracted_rows += len(batch)
                    offset += current_batch_size
                    
                    logger.debug(f"📦 Lote extraído: {len(batch)} registros (Total: {extracted_rows}/{total_rows})")
                    
                    if limit and extracted_rows >= limit:
                        break
            
            self._close_connection(connection)
            logger.info(f"✅ Extracción completada: {extracted_rows} registros de '{table_name}'")
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo datos de '{table_name}': {e}")
            raise
    
    async def get_sample_data(self, database_name: str, table_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Obtener muestra de datos de una tabla"""
        
        try:
            sample_data = []
            async for batch in self.extract_table_data(database_name, table_name, limit, limit=limit):
                sample_data.extend(batch)
                break  # Solo el primer lote
            
            return sample_data[:limit]
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo muestra de '{table_name}': {e}")
            return []
    
    def get_database_names(self) -> List[str]:
        """Obtener lista de nombres de BD configuradas"""
        return [name for name, config in self.config.databases.items() if config.enabled]
    
    async def health_check(self) -> bool:
        """Health check general del manager"""
        try:
            enabled_dbs = self.get_database_names()
            if not enabled_dbs:
                return False
            
            # Test rápido de una BD
            test_db = enabled_dbs[0]
            db_config = self.config.get_database_config(test_db)
            connection = await self._create_connection(db_config)
            
            if connection:
                await self._test_single_connection(connection, test_db)
                self._close_connection(connection)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Health check falló: {e}")
            return False
    
    async def close_connections(self):
        """Cerrar todas las conexiones"""
        try:
            for pool in self.connection_pools.values():
                for conn in pool.connections:
                    self._close_connection(conn)
            
            self.connection_pools.clear()
            logger.info("✅ Todas las conexiones cerradas")
            
        except Exception as e:
            logger.error(f"❌ Error cerrando conexiones: {e}")
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Obtener métricas del database manager"""
        
        metrics = {
            "total_databases": len(self.config.databases),
            "enabled_databases": len(self.get_database_names()),
            "health_status": self.health_status.copy(),
            "connection_pools": len(self.connection_pools)
        }
        
        return metrics


# ================================================================
# EJEMPLO DE USO
# ================================================================

if __name__ == "__main__":
    import asyncio
    from .config import ETLConfig
    
    async def test_database_manager():
        # Configuración de prueba
        config = ETLConfig()
        
        # Inicializar manager
        db_manager = DatabaseManager(config)
        
        # Test conexiones
        results = await db_manager.test_connections()
        print("Resultados de conexión:", results)
        
        # Introspeccionar esquema
        if any(results.values()):
            db_name = next(name for name, success in results.items() if success)
            schema = await db_manager.introspect_schema(db_name)
            print(f"Esquema de '{db_name}':", len(schema["tables"]), "tablas")
            
            # Obtener muestra de datos
            if schema["tables"]:
                table_name = list(schema["tables"].keys())[0]
                sample = await db_manager.get_sample_data(db_name, table_name, 3)
                print(f"Muestra de '{table_name}':", len(sample), "registros")
        
        # Cerrar conexiones
        await db_manager.close_connections()
    
    # Ejecutar test
    asyncio.run(test_database_manager())
