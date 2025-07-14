Hey Benson Webhook – Railway Ready

1. Upload this folder as a ZIP or connect via GitHub
2. Set environment variable:
   GOOGLE_API_KEY = your-real-key
3. Set start command:
   python places_webhook_launchable.py
4. Done. Your webhook will auto-bind to the correct port.

Test routes:
- /                  → Healthcheck
- /healthcheck/env   → Check if API key is set
- /get_venue_info?query=Petco+Park&city=San+Diego
