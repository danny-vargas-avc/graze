# Graze Admin Configuration Guide

This guide explains how to manage Graze app configuration through the Django admin interface.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Filter Configuration](#filter-configuration)
3. [Quick Filters](#quick-filters)
4. [Sort Options](#sort-options)
5. [App Settings](#app-settings)
6. [Restaurant Colors](#restaurant-colors)
7. [Cache Management](#cache-management)
8. [Troubleshooting](#troubleshooting)

---

## Overview

All frontend configuration is managed through Django admin. Changes take effect after users refresh their browser (or after 24 hours when cache expires).

**Admin URL**: `http://your-domain.com/admin/`

**Configuration Sections**:
- **Filter Configurations** - Nutrition filter ranges (calories, protein, etc.)
- **Quick Filters** - Preset filter buttons ("High Protein 40g+", etc.)
- **Sort Options** - Dropdown sort options
- **App Configuration** - Global settings (map defaults, pagination, etc.)
- **Restaurants** - Restaurant brand colors

---

## Filter Configuration

**Location**: Admin → Config → Filter Configurations

Defines the filter ranges that appear in the sidebar (calories, protein, carbs, fat).

### Fields

| Field | Description | Example |
|-------|-------------|---------|
| **Name** | Internal identifier (lowercase, no spaces) | `calories` |
| **Display Name** | Label shown to users | `Calories` |
| **Filter Type** | `range` (min/max) or `max_only` | `range` |
| **Unit** | Unit suffix for labels | `g` (for grams) |
| **Options** | JSON array of filter options (see below) | `[{"label": "0-300", ...}]` |
| **Order** | Display order (lower = first) | `1` |
| **Is Active** | Show/hide this filter | ✓ |

### Options JSON Format

```json
[
  {
    "label": "Any",
    "min": null,
    "max": null
  },
  {
    "label": "0-300",
    "min": 0,
    "max": 300
  },
  {
    "label": "300-500",
    "min": 300,
    "max": 500
  },
  {
    "label": "500-700",
    "min": 500,
    "max": 700
  },
  {
    "label": "700+",
    "min": 700,
    "max": null
  }
]
```

**Notes**:
- `null` means "no limit"
- Always include an "Any" option as the first item
- For `max_only` filters (like carbs), set `min: null` for all options

### Example: Adding a New Filter

**Scenario**: Add a "Sodium" filter

1. Go to **Config → Filter Configurations → Add**
2. Fill in:
   - Name: `sodium`
   - Display Name: `Sodium`
   - Filter Type: `max_only`
   - Unit: `mg`
   - Options:
     ```json
     [
       {"label": "Any", "min": null, "max": null},
       {"label": "Low (0-500mg)", "min": null, "max": 500},
       {"label": "Medium (500-1000mg)", "min": null, "max": 1000},
       {"label": "High (1000mg+)", "min": null, "max": null}
     ]
     ```
   - Order: `5`
   - Is Active: ✓
3. Click **Save**
4. Users see new filter after page refresh

---

## Quick Filters

**Location**: Admin → Config → Quick Filters

Preset filter buttons that appear above the filter accordions.

### Fields

| Field | Description | Example |
|-------|-------------|---------|
| **ID Key** | Unique identifier (slug format) | `high-protein` |
| **Label** | Button text shown to users | `High Protein 40g+` |
| **Filter Params** | JSON object of filter settings (see below) | `{"protein_min": 40}` |
| **Requires Location** | Only show when user has location enabled | ☐ |
| **Order** | Display order (lower = first) | `1` |
| **Is Active** | Show/hide this filter | ✓ |

### Filter Params JSON Format

```json
{
  "protein_min": 40,
  "calories_max": 500,
  "carbs_max": 30,
  "sort": "protein_ratio_desc"
}
```

**Available Parameters**:
- `calories_min`, `calories_max`
- `protein_min`, `protein_max`
- `carbs_min`, `carbs_max`
- `fat_min`, `fat_max`
- `radius` (requires location)
- `sort` (see Sort Options for values)

### Example: Adding "Keto Friendly" Filter

1. Go to **Config → Quick Filters → Add**
2. Fill in:
   - ID Key: `keto-friendly`
   - Label: `Keto Friendly`
   - Filter Params:
     ```json
     {
       "carbs_max": 20,
       "fat_min": 15,
       "sort": "fat_desc"
     }
     ```
   - Requires Location: ☐
   - Order: `5`
   - Is Active: ✓
3. Click **Save**

---

## Sort Options

**Location**: Admin → Config → Sort Options

Dropdown options for sorting dishes.

### Fields

| Field | Description | Example |
|-------|-------------|---------|
| **Value** | Internal sort key (matches backend) | `protein_desc` |
| **Label** | Text shown in dropdown | `Highest Protein` |
| **Requires Location** | Only show when user has location | ☐ |
| **Order** | Display order | `2` |
| **Is Active** | Show/hide this option | ✓ |

### Common Sort Values

| Value | Sorts by... |
|-------|-------------|
| `protein_ratio_desc` | Best protein-to-calorie ratio |
| `protein_desc` | Highest protein |
| `protein_asc` | Lowest protein |
| `calories_asc` | Lowest calories |
| `calories_desc` | Highest calories |
| `carbs_asc` | Lowest carbs |
| `fat_desc` | Highest fat |
| `fat_asc` | Lowest fat |
| `alpha_asc` | Alphabetical (A-Z) |
| `distance_asc` | Nearest (requires location) |

### Example: Adding "Best for Bulking" Sort

1. Go to **Config → Sort Options → Add**
2. Fill in:
   - Value: `calories_protein_desc` (must match backend implementation)
   - Label: `Best for Bulking`
   - Requires Location: ☐
   - Order: `10`
   - Is Active: ✓
3. Click **Save**

**Note**: You must also implement the backend sorting logic for new values.

---

## App Settings

**Location**: Admin → Config → App Configuration

Global app-wide settings (singleton - only one instance exists).

### Map Defaults

| Field | Description | Default |
|-------|-------------|---------|
| **Default Map Center Lng** | Longitude for map center | `-74.0060` (NYC) |
| **Default Map Center Lat** | Latitude for map center | `40.7128` (NYC) |
| **Default Map Zoom** | Initial zoom level (1-20) | `12` |

**Tip**: Use [latlong.net](https://www.latlong.net/) to find coordinates for your city.

### Pagination

| Field | Description | Default |
|-------|-------------|---------|
| **Items Per Page** | Number of dishes loaded per page | `20` |

**Note**: Higher values improve UX but increase load times.

### Filters

| Field | Description | Default |
|-------|-------------|---------|
| **Radius Options** | Available distance filters (JSON array) | `[5, 10, 25, 50]` |
| **Default Sort** | Default sorting when app loads | `protein_ratio_desc` |

**Radius Options Format**:
```json
[5, 10, 25, 50]
```

### Features

| Field | Description | Default |
|-------|-------------|---------|
| **Enable Geolocation** | Show location features | ✓ |
| **Enable Distance Sort** | Show "Nearest" sort option | ✓ |

### Cache Control

| Field | Description | Default |
|-------|-------------|---------|
| **Config Version** | Increment to force cache refresh | `1` |

**How to force refresh**:
1. Change version from `1` to `2`
2. Save
3. All users' cached config becomes invalid
4. They fetch fresh config on next load

---

## Restaurant Colors

**Location**: Admin → Restaurants → [Restaurant Name]

Each restaurant has a brand color used for map markers.

### Field

| Field | Description | Example |
|-------|-------------|---------|
| **Brand Color** | Hex color code | `#A81612` |

### Current Colors

| Restaurant | Color | Hex |
|------------|-------|-----|
| Chipotle | 🔴 Dark Red | `#A81612` |
| CAVA | 🟠 Orange | `#F4A261` |
| Sweetgreen | 🟢 Green | `#6DBF4B` |
| Panera | 🟢 Olive Green | `#5C8B3E` |
| Chick-fil-A | 🔴 Red | `#E51937` |
| Default | 🔵 Blue | `#3B82F6` |

**Tip**: Use [htmlcolorcodes.com](https://htmlcolorcodes.com/) to pick colors.

---

## Cache Management

### How Caching Works

1. **First Load**: Frontend fetches config from API
2. **Cache**: Saves to browser localStorage (24 hour TTL)
3. **Subsequent Loads**: Uses cached config (no API call)
4. **Expiry**: After 24 hours, fetches fresh config

### Force Cache Refresh

**Method 1: Increment Version**
1. Go to **App Configuration**
2. Increment **Config Version** (e.g., `1` → `2`)
3. Save
4. All users get fresh config on next load

**Method 2: Clear Browser Cache**
- Users can clear browser data
- Or use Incognito/Private mode

### Troubleshooting Cache Issues

**Problem**: Changes not appearing for users

**Solutions**:
1. Increment Config Version
2. Wait 24 hours (cache expires)
3. Ask users to hard refresh (Ctrl+Shift+R / Cmd+Shift+R)
4. Check browser console for errors

---

## Troubleshooting

### Changes Not Appearing

**Check**:
- Is the item marked **Is Active**? ✓
- Did you increment **Config Version**?
- Is the JSON format correct? (use validator: [jsonlint.com](https://jsonlint.com/))
- Are there browser console errors?

### Invalid JSON Error

**Symptoms**: Admin shows "Invalid JSON" error

**Fix**:
1. Copy JSON to [jsonlint.com](https://jsonlint.com/)
2. Fix errors (missing commas, quotes, etc.)
3. Paste corrected JSON back

**Common mistakes**:
- Missing quotes around strings
- Trailing comma in arrays
- Using single quotes instead of double quotes
- Missing brackets `[]` or braces `{}`

### Filter Not Working

**Check Backend**:
- Is the filter parameter supported by API?
- Check API documentation: `/api/docs/`
- Test API directly: `GET /api/v1/dishes?protein_min=40`

**Check Frontend**:
- Browser console for errors
- Network tab - is config being fetched?
- localStorage - is config cached correctly?

### Restaurant Color Not Updating

**Check**:
1. Color is valid hex code (e.g., `#A81612`)
2. Restaurant slug matches exactly (case-sensitive)
3. Clear browser cache
4. Check map markers after page refresh

---

## Best Practices

### ✅ Do

- Test changes in staging before production
- Use descriptive labels that users understand
- Keep filter ranges reasonable (don't overwhelm users)
- Document custom changes in comments
- Increment version for critical updates

### ❌ Don't

- Don't create too many quick filters (max 5-6)
- Don't use extreme filter ranges (e.g., 0-10000)
- Don't change default sort without testing
- Don't delete filters users depend on
- Don't forget to activate new items (Is Active ✓)

---

## Getting Help

**For technical issues**:
- Check browser console (F12)
- Check backend logs
- Contact dev team

**For configuration questions**:
- Refer to this guide
- Check existing configurations as examples
- Test in staging first

---

## Appendix: JSON Examples

### Complete Filter Configuration

```json
{
  "name": "calories",
  "display_name": "Calories",
  "filter_type": "range",
  "unit": "",
  "options": [
    {"label": "Any", "min": null, "max": null},
    {"label": "0-300", "min": 0, "max": 300},
    {"label": "300-500", "min": 300, "max": 500},
    {"label": "500-700", "min": 500, "max": 700},
    {"label": "700+", "min": 700, "max": null}
  ],
  "order": 1,
  "is_active": true
}
```

### Complete Quick Filter

```json
{
  "id_key": "high-protein",
  "label": "High Protein 40g+",
  "filter_params": {
    "protein_min": 40,
    "sort": "protein_desc"
  },
  "requires_location": false,
  "order": 1,
  "is_active": true
}
```

### Complete App Settings

```json
{
  "default_map_center_lng": -74.0060,
  "default_map_center_lat": 40.7128,
  "default_map_zoom": 12,
  "items_per_page": 20,
  "radius_options": [5, 10, 25, 50],
  "default_sort": "protein_ratio_desc",
  "enable_geolocation": true,
  "enable_distance_sort": true,
  "config_version": 1
}
```

---

**Last Updated**: 2026-01-31
**Version**: 1.0
