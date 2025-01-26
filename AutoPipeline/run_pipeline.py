from retail_pipeline import RetailAnalysisPipeline

#creating a function to run the pipeline directly
def main():
    pipeline = RetailAnalysisPipeline()
    pipeline.run_pipeline()

if __name__ == "__main__":
    main()