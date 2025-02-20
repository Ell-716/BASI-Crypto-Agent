from backend.app.tasks import update_historical_data, update_technical_indicators


if __name__ == "__main__":
    print("🔄 Running cron job: updating historical data & indicators...")
    update_historical_data()
    update_technical_indicators()
    print("✅ Cron job completed successfully.")
