from database import db


def get_social_stats(language):
    try:
        result = db.engine.execute(
            "SELECT Distinct ON (name) id, name, timestamp, subscribed_count FROM social_stat ORDER BY name, timestamp DESC;"
        )

        def filter_social_stats(stat):
            general_stats = [
                "Discord",
                "Telegram",
                "Weibo",
                "Wechat",
                "KaKao plus friends",
                "Facebook",
                "Twitter",
                "Instagram",
                "Youtube",
                "Reddit",
                "Telegram (Korean)",
                "Telegram (Vietnam)",
                "Telegram (Indonesia)",
                "Telegram (Russia)",
                "Telegram (Spanish)",
                "Telegram (Turkish)",
                "Telegram (China)",
                "Medium",
            ]
            if stat["name"] in general_stats:
                return True
            else:
                return False

        dict_result = [dict(row) for row in result]
        return list(filter(filter_social_stats, dict_result))
    except:
        return None
