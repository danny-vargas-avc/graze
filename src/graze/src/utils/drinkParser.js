/**
 * Parse drink variant names into base drink, milk type, and size.
 * Naming convention: "Base Drink - milk type (Size)"
 */

const VALID_SIZES = ['Short', 'Tall', 'Grande', 'Venti', 'Doppio']
const VALID_MILKS = [
  'semi skimmed milk', 'skimmed milk', 'whole milk',
  'soya drink', 'almond drink', 'oat drink', 'coconut drink',
]

const VARIANT_REGEX = /^(.+?)\s*-\s*(.+?)\s*\(([^)]+)\)$/

/**
 * Parse a dish name to extract drink variant info.
 * @param {string} name - The full dish name
 * @returns {{ baseName: string, milkType: string, size: string } | null}
 */
export function parseDrinkVariant(name) {
  const match = name.match(VARIANT_REGEX)
  if (!match) return null

  const [, baseName, milkType, size] = match
  if (!VALID_SIZES.includes(size) || !VALID_MILKS.includes(milkType)) return null

  return { baseName: baseName.trim(), milkType, size }
}

/**
 * Group an array of dishes into base drinks with their available variants.
 * @param {Array} dishes - All dishes from a restaurant
 * @returns {{ baseDrinks: Array, foodDishes: Array }}
 */
export function groupDrinkVariants(dishes) {
  const baseDrinksMap = {}
  const foodDishes = []

  for (const dish of dishes) {
    const parsed = parseDrinkVariant(dish.name)
    if (!parsed) {
      foodDishes.push(dish)
      continue
    }

    const { baseName, milkType, size } = parsed

    if (!baseDrinksMap[baseName]) {
      baseDrinksMap[baseName] = {
        baseName,
        category: dish.category,
        sizes: new Set(),
        milks: new Set(),
        variants: {},
      }
    }

    const entry = baseDrinksMap[baseName]
    entry.sizes.add(size)
    entry.milks.add(milkType)
    entry.variants[`${size}|${milkType}`] = dish
  }

  // Convert sets to sorted arrays, order sizes logically
  const sizeOrder = { Short: 0, Tall: 1, Grande: 2, Venti: 3, Doppio: 4 }
  const baseDrinks = Object.values(baseDrinksMap).map(entry => ({
    ...entry,
    sizes: [...entry.sizes].sort((a, b) => (sizeOrder[a] ?? 99) - (sizeOrder[b] ?? 99)),
    milks: [...entry.milks].sort(),
  }))

  return { baseDrinks, foodDishes }
}

/**
 * Look up a specific variant's nutrition data.
 * @param {object} baseDrink - A baseDrink entry from groupDrinkVariants
 * @param {string} size - Selected size
 * @param {string} milkType - Selected milk type
 * @returns {object|null} The matching dish with full nutrition, or null
 */
export function lookupVariant(baseDrink, size, milkType) {
  return baseDrink.variants[`${size}|${milkType}`] || null
}
