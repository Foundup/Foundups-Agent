# GCC Shipping Tracker Skill

## Purpose
Real-time shipping traffic visualization for the Gulf Cooperation Council (GCC) region, focusing on the Strait of Hormuz - the world's most critical oil chokepoint.

**BOOT LAYER**: Default visual for antifaFM stream startup. Runs 10-minute rotation cycle until stakeholder (moderator) or delegate (managing moderator) intervenes.

## Boot Layer Mode
```bash
# Start daemon (boot visual - 10 min rotation)
python executor.py --daemon

# Stakeholder override (pause daemon)
python executor.py --override

# Clear override (resume daemon)
python executor.py --clear-override
```

## Command
```bash
/gcc                    # Show current ship traffic summary
/gcc --daemon           # Boot layer mode (10-min rotation)
/gcc --map              # Open live map in browser
/gcc --tankers          # Filter oil tankers only
/gcc --alerts           # Show naval/military activity
```

## Rotation Cycle (Boot Layer)
| Minute | View | Description |
|--------|------|-------------|
| 0-10 | Hormuz | Strait of Hormuz close-up |
| 10-20 | Gulf | Full Persian Gulf view |
| 20-30 | Tankers | Oil tanker filter |
| (repeat) | ... | Until stakeholder override |

## Data Sources

| Source | Type | Update Frequency |
|--------|------|------------------|
| **MarineTraffic** | AIS tracking | Real-time |
| **VesselFinder** | AIS + satellite | Near real-time |
| **FleetMon** | Commercial API | 5-minute |

## Coverage Area
- **Strait of Hormuz**: 21-35 km wide chokepoint
- **Persian Gulf**: Full coverage
- **Gulf of Oman**: Approach lanes
- **Key Ports**: Dubai, Abu Dhabi, Doha, Bahrain, Kuwait

## Ship Categories
| Category | Significance |
|----------|--------------|
| VLCC/ULCC | Very/Ultra Large Crude Carriers (oil) |
| LNG | Liquefied Natural Gas tankers |
| Container | Commercial shipping |
| Naval | Military vessels (if AIS active) |
| Bulk | Dry cargo |

## Output Format
```json
{
  "timestamp": "2026-03-11T13:00:00Z",
  "region": "strait_of_hormuz",
  "vessel_count": 45,
  "by_type": {
    "tanker": 28,
    "lng": 8,
    "container": 5,
    "bulk": 4
  },
  "alerts": [
    {"type": "high_traffic", "area": "inbound_lane"}
  ],
  "map_url": "https://www.marinetraffic.com/..."
}
```

## Integration with antifaFM
- Can overlay shipping data on stream
- Breaking news: unusual naval activity
- Oil market correlation alerts

## WSP Compliance
- WSP 27: Universal DAE Architecture
- WSP 103: CLI Interface Standard
- WSP 60: Signal Quality (real-time data)
