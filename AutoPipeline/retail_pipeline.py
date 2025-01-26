#Installing required Libraries
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_squared_error
import logging

#Setting up logging for ease
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('retail_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RetailAnalysisPipeline:
    def __init__(self):
        """Initialize the pipeline"""
        self.sales_df = None
        self.store_df = None
        self.customer_df = None
        self.merged_df = None
        
    def load_data(self):
        """Load data from CSV files"""
        try:
            logger.info("Loading data...")
            
            # Load each dataset
            self.sales_df = pd.read_csv('sales_data.csv')
            self.store_df = pd.read_csv('store_data.csv')
            self.customer_df = pd.read_csv('customer_data_cleaned.csv')
            
            # Log data shapes
            logger.info(f"Sales data shape: {self.sales_df.shape}")
            logger.info(f"Store data shape: {self.store_df.shape}")
            logger.info(f"Customer data shape: {self.customer_df.shape}")
            
            logger.info("Data loaded successfully")
            return True
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            return False
    
    def preprocess_data(self):
        """Preprocess and merge datasets"""
        try:
            logger.info("Preprocessing data...")
            
            # 1. Standardizing store IDs
            #Converting store_id in store_df to match storeID format in sales_df
            self.store_df['store_id'] = self.store_df['store_id'].str.upper()
            
            # 2. Converting date format across the data
            self.sales_df['date'] = pd.to_datetime(self.sales_df['date'])
            self.customer_df['date'] = pd.to_datetime(self.customer_df['date'])
            
            # 3. Merging sales and store data as per the process
            logger.info("Merging sales and store data...")
            self.merged_df = self.sales_df.merge(
                self.store_df,
                left_on='storeID',
                right_on='store_id',
                how='left'
            )
            
            #Merging the results
            logger.info(f"Merged data shape after store merge: {self.merged_df.shape}")
            
            #Adding customer metrics
            daily_customer_metrics = self.customer_df.groupby('date').agg({
                'num_items': 'mean',
                'avg_price': 'mean'
            }).reset_index()
            
            #Merging customer metrics
            self.merged_df = self.merged_df.merge(
                daily_customer_metrics,
                on='date',
                how='left'
            )
            
            #Calculating additional metrics
            self.merged_df['total_sales'] = self.merged_df['total_amount']
            self.merged_df['profit'] = self.merged_df['total_amount'] * self.merged_df['profit_margin']
            
            #Dropping duplicate columns
            self.merged_df = self.merged_df.drop('store_id', axis=1)
            
            logger.info(f"Final merged data shape: {self.merged_df.shape}")
            logger.info("Data preprocessing completed")
            return True
            
        except Exception as e:
            logger.error(f"Error preprocessing data: {str(e)}")
            logger.error("Full error details:", exc_info=True)
            return False
    
    def analyze_sales(self):
        """Analyze sales patterns"""
        try:
            logger.info("Analyzing sales patterns...")
            
            #Daily sales analysis - Something I am interested in
            daily_sales = self.merged_df.groupby('date').agg({
                'total_sales': 'sum',
                'profit': 'sum',
                'items_count': 'sum'
            }).reset_index()
            
            #Storing performance for accounting and visualization
            store_performance = self.merged_df.groupby('storeID').agg({
                'total_sales': 'sum',
                'profit': 'sum',
                'items_count': 'sum'
            }).reset_index()
            
            #Saving results in .csv file
            daily_sales.to_csv('daily_sales_analysis.csv', index=False)
            store_performance.to_csv('store_performance.csv', index=False)
            
            logger.info("Sales analysis completed and saved")
            return True
        except Exception as e:
            logger.error(f"Error in sales analysis: {str(e)}")
            return False
    
    def run_pipeline(self):
        """Run the complete analysis pipeline"""
        if self.load_data() and self.preprocess_data():
            self.analyze_sales()
            logger.info("Pipeline completed successfully")
        else:
            logger.error("Pipeline failed")

if __name__ == "__main__":
    pipeline = RetailAnalysisPipeline()
    pipeline.run_pipeline()