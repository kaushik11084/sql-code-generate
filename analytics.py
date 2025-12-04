import os
import segment.analytics as analytics

# Analytics
analytics.write_key = os.getenv("SEGMENT_KEY")

# Default user for analytics
userId = "default"

def on_error(error, items):
    print("An error occurred in analytics call:", error)
analytics.on_error = on_error

def sendTrackEvent(user, prop_dict: dict, event_name):
    properts = {
        "text": "Brief builder",
        "productTitle": "Digital Self-Serve Co-Create Experience",
        "objectType": "dsce-wx-app",
        "data": prop_dict
    }
    analytics.track(user or userId, "UI Interaction", properts)