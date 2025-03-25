from typing import List, Optional
from app.data.db_modules.stock_modules.stock_basic.stock_company import StockCompanyData


class StockCompanyCRUD:
    """
    CRUD operations for stock company data.
    
    Provides methods to create, read, update, and delete stock company records in the database.
    """

    def __init__(self, db):
        self.db = db

    async def create_company(self, data: StockCompanyData) -> str:
        """
        Create a new stock company record in the database.
        
        Args:
            data (StockCompanyData): The company data to insert
            
        Returns:
            str: The ts_code of the newly created record
        """
        query = """
            INSERT INTO stock_company (
                ts_code, com_name, com_id, exchange, chairman, manager, 
                secretary, reg_capital, setup_date, province, city, 
                introduction, website, email, office, employees, 
                main_business, business_scope
            ) VALUES (
                $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, 
                $13, $14, $15, $16, $17, $18
            ) RETURNING ts_code
        """
        values = [
            data.ts_code,
            data.com_name,
            data.com_id,
            data.exchange,
            data.chairman,
            data.manager,
            data.secretary,
            data.reg_capital,
            data.setup_date,
            data.province,
            data.city,
            data.introduction,
            data.website,
            data.email,
            data.office,
            data.employees,
            data.main_business,
            data.business_scope
        ]
        return await self.db.fetchval(query, *values)

    async def get_company_by_ts_code(self, ts_code: str) -> Optional[StockCompanyData]:
        """
        Retrieve a stock company record by its TS code.
        
        Args:
            ts_code (str): The TS code of the company to retrieve
            
        Returns:
            StockCompanyData | None: The company data if found, None otherwise
        """
        query = "SELECT * FROM stock_company WHERE ts_code = $1"
        row = await self.db.fetchrow(query, ts_code)
        return StockCompanyData(**row) if row else None
    
    async def get_company_by_com_id(self, com_id: str) -> Optional[StockCompanyData]:
        """
        Retrieve a stock company record by its company ID (social credit code).
        
        Args:
            com_id (str): The company ID to retrieve
            
        Returns:
            StockCompanyData | None: The company data if found, None otherwise
        """
        query = "SELECT * FROM stock_company WHERE com_id = $1"
        row = await self.db.fetchrow(query, com_id)
        return StockCompanyData(**row) if row else None
    
    async def update_company(self, ts_code: str, updates: dict) -> bool:
        """
        Update a stock company record by its TS code.
        
        Args:
            ts_code (str): The TS code of the company to update
            updates (dict): Dictionary of fields to update and their new values
            
        Returns:
            bool: True if the update was successful, False otherwise
        """
        set_values = ','.join([f"{key} = ${idx + 2}" for idx, key in enumerate(updates.keys())])
        query = f"""
            UPDATE stock_company
            SET {set_values}
            WHERE ts_code = $1
        """
        result = await self.db.execute(query, ts_code, *updates.values())
        return 'UPDATE' in result
    
    async def delete_company(self, ts_code: str) -> bool:
        """
        Delete a stock company record by its TS code.
        
        Args:
            ts_code (str): The TS code of the company to delete
            
        Returns:
            bool: True if the deletion was successful, False otherwise
        """
        query = "DELETE FROM stock_company WHERE ts_code = $1"
        result = await self.db.execute(query, ts_code)
        return 'DELETE' in result
    
    async def list_companies(self, limit: int = 100, offset: int = 0) -> List[StockCompanyData]:
        """
        List stock companies with pagination.
        
        Args:
            limit (int): Maximum number of records to retrieve
            offset (int): Number of records to skip
            
        Returns:
            list[StockCompanyData]: List of company data
        """
        query = "SELECT * FROM stock_company ORDER BY ts_code LIMIT $1 OFFSET $2"
        rows = await self.db.fetch(query, limit, offset)
        return [StockCompanyData(**row) for row in rows]
    
    async def list_companies_by_province(self, province: str) -> List[StockCompanyData]:
        """
        List all companies in a specific province.
        
        Args:
            province (str): The province to filter by
            
        Returns:
            list[StockCompanyData]: List of company data
        """
        query = "SELECT * FROM stock_company WHERE province = $1 ORDER BY ts_code"
        rows = await self.db.fetch(query, province)
        return [StockCompanyData(**row) for row in rows]
    
    async def list_exchange_companies(self, exchange: str) -> List[StockCompanyData]:
        """
        List all companies listed on a specific exchange.
        
        Args:
            exchange (str): The exchange code to filter by
            
        Returns:
            list[StockCompanyData]: List of company data
        """
        query = "SELECT * FROM stock_company WHERE exchange = $1 ORDER BY ts_code"
        rows = await self.db.fetch(query, exchange)
        return [StockCompanyData(**row) for row in rows]
    
    async def search_companies(self, search_term: str, limit: int = 100) -> List[StockCompanyData]:
        """
        Search for companies by name or business.
        
        Args:
            search_term (str): Term to search for
            limit (int): Maximum number of records to retrieve
            
        Returns:
            list[StockCompanyData]: List of company data matching the search term
        """
        query = """
            SELECT * FROM stock_company 
            WHERE com_name ILIKE $1 
            OR main_business ILIKE $1 
            OR business_scope ILIKE $1
            ORDER BY ts_code 
            LIMIT $2
        """
        search_pattern = f"%{search_term}%"
        rows = await self.db.fetch(query, search_pattern, limit)
        return [StockCompanyData(**row) for row in rows]
    
    async def get_company_count_by_province(self) -> dict:
        """
        Get the count of companies by province.
        
        Returns:
            dict: Dictionary mapping province name to company count
        """
        query = """
            SELECT province, COUNT(*) as count
            FROM stock_company
            WHERE province IS NOT NULL
            GROUP BY province
            ORDER BY count DESC
        """
        rows = await self.db.fetch(query)
        return {row['province']: row['count'] for row in rows}