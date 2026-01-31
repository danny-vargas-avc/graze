# Configuration System Testing Checklist

Use this checklist to verify the frontend configuration system is working correctly.

## ✅ Pre-Testing Setup

- [ ] Run `cd src/graze && yarn dev`
- [ ] Open browser to `http://localhost:5173`
- [ ] Open browser DevTools (F12) → Console tab
- [ ] Open DevTools → Application tab → Local Storage

---

## 1️⃣ Config Store Initialization

### Test: App loads without errors

**Steps**:
1. Refresh the page
2. Check console for config messages

**Expected**:
- Console shows: `"Using fallback configuration"` (since no backend yet)
- No errors in console
- App loads normally

**Verify**:
- [ ] No JavaScript errors
- [ ] Console shows config fallback message
- [ ] App renders correctly

---

## 2️⃣ Filter Options

### Test: Filters load from config store

**Location**: Search page sidebar

**Steps**:
1. Go to `/search`
2. Open filter accordions (Calories, Protein, Carbs, Fat)

**Expected**:
Each filter shows options:
- Calories: Any, 0-300, 300-500, 500-700, 700+
- Protein: Any, 0-20g, 20-40g, 40-60g, 60g+
- Carbs: Any, 0-30g, 30-60g, 60-100g, 100g+
- Fat: Any, 0-15g, 15-30g, 30-50g, 50g+

**Verify**:
- [ ] All filter options appear
- [ ] Options are correctly labeled
- [ ] Clicking options filters dishes
- [ ] URL updates with filter params

---

## 3️⃣ Quick Filters

### Test: Quick filter buttons work

**Location**: Search page, above filter accordions

**Steps**:
1. Check for quick filter chips
2. Click each filter button

**Expected Quick Filters**:
- High Protein 40g+ (always visible)
- Under 500 cal (always visible)
- Best Ratio (always visible)
- Low Carb (always visible)
- Nearby 5 mi (only if location enabled)

**Verify**:
- [ ] Quick filters appear
- [ ] Clicking applies correct filters
- [ ] Dishes update accordingly
- [ ] "Nearby 5 mi" hidden when no location
- [ ] "Nearby 5 mi" appears after enabling location

---

## 4️⃣ Sort Options

### Test: Sort dropdown loads from config

**Location**: Search page header, right side

**Steps**:
1. Click sort dropdown
2. Check all options

**Expected Options**:
- Best Protein/Cal
- Highest Protein
- Lowest Protein
- Lowest Calories
- Highest Calories
- Lowest Carbs
- Highest Fat
- Lowest Fat
- A-Z
- Nearest (only with location)

**Verify**:
- [ ] All sort options appear
- [ ] Options are correctly labeled
- [ ] Selecting an option sorts dishes
- [ ] "Nearest" hidden when no location
- [ ] "Nearest" appears after enabling location

---

## 5️⃣ Map Configuration

### Test: Map uses config defaults

**Location**: Search page map view

**Steps**:
1. Switch to map view (if mobile)
2. Check map center and zoom

**Expected**:
- Map centers on NYC: `[-74.0060, 40.7128]`
- Zoom level: `12`

**Verify**:
- [ ] Map loads correctly
- [ ] Default center is NYC
- [ ] Default zoom looks reasonable
- [ ] Map is interactive

---

## 6️⃣ Restaurant Colors

### Test: Map markers use brand colors

**Location**: Search page map view

**Steps**:
1. View map with restaurant markers
2. Check marker colors

**Expected Colors**:
- Chipotle: Red (#A81612)
- CAVA: Orange (#F4A261)
- Sweetgreen: Green (#6DBF4B)
- Panera: Olive (#5C8B3E)
- Chick-fil-A: Red (#E51937)
- Other: Blue (#3B82F6)

**Verify**:
- [ ] Markers have colors
- [ ] Colors match restaurant brands
- [ ] Default color for unknown restaurants

---

## 7️⃣ Radius Options

### Test: Distance filters from config

**Location**: Location filters (if exists)

**Steps**:
1. Enable location
2. Check radius filter options

**Expected Options**: 5 mi, 10 mi, 25 mi, 50 mi

**Verify**:
- [ ] Radius options appear
- [ ] Options: 5, 10, 25, 50 miles
- [ ] Selecting radius filters dishes

---

## 8️⃣ Pagination

### Test: Items per page from config

**Location**: Dish list scroll

**Steps**:
1. Scroll to bottom of dish list
2. Check "Load More" button
3. Count initial dishes loaded

**Expected**: 20 dishes loaded initially

**Verify**:
- [ ] Initial load shows 20 dishes
- [ ] "Load More" loads 20 more
- [ ] Pagination works correctly

---

## 9️⃣ LocalStorage Cache

### Test: Config cached correctly

**Location**: DevTools → Application → Local Storage

**Steps**:
1. Refresh page
2. Check Local Storage
3. Look for `graze_config` key

**Expected**:
```json
{
  "filters": [...],
  "quickFilters": [...],
  "sortOptions": [...],
  "appSettings": {...},
  "restaurantColors": {...},
  "version": 1,
  "lastFetched": 1706745600000
}
```

**Verify**:
- [ ] `graze_config` key exists
- [ ] Contains all config data
- [ ] `lastFetched` timestamp present
- [ ] Data is valid JSON

---

## 🔟 Cache Refresh

### Test: Cache expires after 24 hours

**Steps**:
1. Open DevTools → Console
2. Run: `localStorage.removeItem('graze_config')`
3. Refresh page
4. Check console for "Using fallback configuration"

**Expected**:
- Cache cleared
- App fetches config (or uses fallback)
- App still works

**Verify**:
- [ ] Clearing cache works
- [ ] App fetches fresh config
- [ ] Fallback config works

---

## 1️⃣1️⃣ Component Updates

### Test: All components use config store

**Check these files use configStore**:

**SearchView.vue**:
- [ ] Imports `useConfigStore`
- [ ] Filter options from `configStore.getFilterOptions()`
- [ ] Quick filters from `configStore.getQuickFilters()`
- [ ] Map center from `configStore.appSettings.default_map_center`
- [ ] Map zoom from `configStore.appSettings.default_map_zoom`

**DishSearchView.vue**:
- [ ] Same as SearchView

**SortDropdown.vue**:
- [ ] Options from `configStore.getSortOptions()`

**MapView.vue**:
- [ ] Restaurant colors from `configStore.getRestaurantColor()`

**LocationFilters.vue**:
- [ ] Radius options from `configStore.appSettings.radius_options`

**stores/dishes.js**:
- [ ] Default sort from `configStore.appSettings.default_sort`
- [ ] Items per page from `configStore.appSettings.items_per_page`
- [ ] Quick filters use `configStore.getQuickFilterById()`

**App.vue**:
- [ ] Calls `configStore.fetchConfig()` on mount

---

## 1️⃣2️⃣ Error Handling

### Test: Graceful fallback when config fails

**Steps**:
1. Simulate API failure (disconnect network)
2. Clear cache: `localStorage.removeItem('graze_config')`
3. Refresh page

**Expected**:
- Console shows: "Failed to fetch config from API, using fallback"
- App still loads with hardcoded config
- All features work normally

**Verify**:
- [ ] App loads without crashing
- [ ] Fallback config used
- [ ] All filters/options available
- [ ] Warning logged in console

---

## 1️⃣3️⃣ Performance

### Test: Config doesn't slow down app

**Steps**:
1. Open DevTools → Network tab
2. Refresh page
3. Check config API call

**Expected**:
- Config loaded from cache (no API call)
- Or API call completes in < 500ms
- Page renders immediately (no blocking)

**Verify**:
- [ ] Page loads quickly
- [ ] No noticeable delay
- [ ] Cache prevents unnecessary API calls

---

## 🐛 Known Issues

### Issue: Config API endpoint not implemented yet

**Symptom**: Console shows "Failed to fetch config"

**Status**: Expected (backend not implemented)

**Workaround**: App uses fallback config automatically

**Resolution**: Implement backend endpoints (Tasks #1-4)

---

## 📝 Test Results

**Date Tested**: _________________

**Tester**: _________________

**Browser**: Chrome / Firefox / Safari (circle one)

**Overall Result**: ✅ Pass / ❌ Fail

**Notes**:
```
[Add any issues, observations, or comments here]
```

---

## 🚀 Next Steps After Testing

If all tests pass:
- [ ] Mark Task #14 complete
- [ ] Move to Task #15 (Cache invalidation)
- [ ] Start backend implementation (Tasks #1-4)

If tests fail:
- [ ] Document failures
- [ ] Create bug tickets
- [ ] Fix issues before proceeding

---

**Testing Checklist Version**: 1.0
**Last Updated**: 2026-01-31
