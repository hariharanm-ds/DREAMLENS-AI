import urllib.request
import urllib.parse
import re
import json
import logging
import random

_YT_CACHE = {}

def search_live_youtube_videos(query: str, max_results: int = 6) -> list:
    """
    Performs a fast cached or live YouTube search for dream-related fantasy videos.
    """
    clean_query = query.strip()
    cache_key = clean_query.lower()
    if cache_key in _YT_CACHE:
        return _YT_CACHE[cache_key][:max_results]

    search_term = f"{clean_query} dream fantasy" if "dream" not in clean_query.lower() else clean_query
    url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(search_term)}"
    
    videos = []
    seen_ids = set()
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9"
            }
        )
        with urllib.request.urlopen(req, timeout=3.5) as response:
            html = response.read().decode("utf-8", errors="ignore")
            
            # Method 1: Extract from ytInitialData
            match = re.search(r'var ytInitialData = ({.*?});</script>', html)
            if match:
                try:
                    data = json.loads(match.group(1))
                    contents = (
                        data.get("contents", {})
                        .get("twoColumnSearchResultsRenderer", {})
                        .get("primaryContents", {})
                        .get("sectionListRenderer", {})
                        .get("contents", [{}])[0]
                        .get("itemSectionRenderer", {})
                        .get("contents", [])
                    )
                    
                    for item in contents:
                        v = item.get("videoRenderer")
                        if v:
                            vid_id = v.get("videoId")
                            title_runs = v.get("title", {}).get("runs", [])
                            title_text = title_runs[0].get("text", "") if title_runs else ""
                            channel_runs = v.get("ownerText", {}).get("runs", [])
                            channel_text = channel_runs[0].get("text", "Dream Cinema") if channel_runs else "Dream Cinema"
                            duration_text = v.get("lengthText", {}).get("simpleText", "12:45")
                            desc_runs = v.get("detailedMetadataSnippets", [{}])[0].get("snippetText", {}).get("runs", [])
                            desc_text = desc_runs[0].get("text", "") if desc_runs else f"Fantasy exploration video relating to {query}."
                            
                            if vid_id and title_text and vid_id not in seen_ids:
                                seen_ids.add(vid_id)
                                genre = "fantasy"
                                t_lower = (title_text + " " + desc_text).lower()
                                if "lucid" in t_lower or "technique" in t_lower or "wake" in t_lower:
                                    genre = "lucid"
                                elif "ambient" in t_lower or "sleep" in t_lower or "music" in t_lower or "sound" in t_lower:
                                    genre = "ambient"
                                elif "science" in t_lower or "psychology" in t_lower or "meaning" in t_lower or "freud" in t_lower:
                                    genre = "mystery"
                                elif "adventure" in t_lower or "journey" in t_lower or "quest" in t_lower:
                                    genre = "adventure"

                                badge_map = {
                                    "fantasy": "badge-purple",
                                    "lucid": "badge-cyan",
                                    "ambient": "badge-green",
                                    "mystery": "badge-pink",
                                    "adventure": "badge-purple"
                                }

                                videos.append({
                                    "ytId": vid_id,
                                    "title": title_text,
                                    "channel": channel_text,
                                    "desc": desc_text,
                                    "genre": genre,
                                    "duration": duration_text,
                                    "badgeClass": badge_map.get(genre, "badge-purple"),
                                    "badgeLabel": genre.capitalize()
                                })
                                if len(videos) >= max_results:
                                    break
                except Exception as je:
                    logging.warning(f"Error parsing ytInitialData: {je}")

            # Method 2: Fast Regex Fallback for video IDs if JSON parsing didn't find enough
            if len(videos) < max_results:
                raw_matches = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
                for rid in raw_matches:
                    if rid not in seen_ids:
                        seen_ids.add(rid)
                        videos.append({
                            "ytId": rid,
                            "title": f"Dream Exploration & Fantasy: {clean_query.title()}",
                            "channel": "Dream Insights Cinema",
                            "desc": f"Experience cinematic reflections and deep archetypal fantasy journeys for {clean_query}.",
                            "genre": "fantasy",
                            "duration": "18:30",
                            "badgeClass": "badge-purple",
                            "badgeLabel": "Fantasy"
                        })
                        if len(videos) >= max_results:
                            break
    except Exception as e:
        logging.warning(f"Live YouTube search fallback: {e}")

    # Fallback to curated catalog if needed
    if len(videos) < 4:
        from services.pipeline import BASE_YOUTUBE_CATALOG
        for item in BASE_YOUTUBE_CATALOG:
            if item["ytId"] not in seen_ids:
                seen_ids.add(item["ytId"])
                videos.append(item)
                if len(videos) >= max_results:
                    break

    return videos[:max_results]


def generate_dream_image_url(dream_text: str, scene_type: str = "dreamscape", seed: int = None) -> str:
    """
    Generates an instant, crystal-clear photorealistic AI fantasy artwork URL tailored specifically
    to the user's dream description using the high-resolution Pollinations AI engine.
    """
    if not seed:
        seed = random.randint(1000, 99999)

    clean_text = dream_text.replace('"', '').replace('\n', ' ').strip()[:140]
    
    style_prompts = {
        "dreamscape": f"Hyperrealistic masterpiece 8k, cinematic fantasy art of {clean_text}, magical bioluminescent glow, ultra detailed concept art, trending on ArtStation, unreal engine 5 render",
        "stage1": f"Cinematic atmospheric fantasy scene of {clean_text}, ethereal mist, dramatic volumetric lighting, 8k resolution, detailed digital illustration",
        "stage2": f"Enchanted glowing fantasy revelation in {clean_text}, radiant magical aura, vibrant crystals, high definition fantasy art",
        "stage3": f"Epic cinematic climax of {clean_text}, celestial energy rays, dramatic perspective, hyper-detailed fantasy art, octane render",
        "stage4": f"Serene tranquil fantasy resolution of {clean_text}, radiant golden sunlight, peaceful ethereal dreamscape, masterpiece painting",
        "scenario": f"Empowered victorious alternative timeline of {clean_text}, triumphant heroic glow, golden celestial aura, 8k cinematic concept art"
    }

    prompt = style_prompts.get(scene_type, style_prompts["dreamscape"])
    encoded = urllib.parse.quote(prompt)
    return f"https://image.pollinations.ai/prompt/{encoded}?width=800&height=450&nologo=true&enhance=true&model=flux&seed={seed}"
