"""Import BYO component data from nutrition PDFs for all BYO restaurants."""
import os
import django
from django.core.management.base import BaseCommand

BYO_DATA = {
    'chipotle': [
        # Bases
        ('base', 'Cilantro-Lime White Rice', 210, 4, 40, 4, 1, 350, 0, 1),
        ('base', 'Cilantro-Lime Brown Rice', 210, 4, 36, 6, 2, 190, 0, 0),
        ('base', 'Black Beans', 130, 8, 22, 1.5, 7, 210, 2, 0),
        ('base', 'Pinto Beans', 130, 8, 21, 1.5, 8, 210, 1, 0),
        ('base', 'Supergreens Salad Mix', 15, 1, 3, 0, 2, 15, 1, 0),
        ('base', 'Flour Tortilla (Burrito)', 320, 8, 50, 9, 3, 600, 0, 0.5),
        ('base', 'Crispy Corn Tortilla (3)', 210, 3, 30, 9, 3, 0, 0, 0),
        # Proteins
        ('protein', 'Chicken', 180, 32, 0, 7, 0, 310, 0, 3),
        ('protein', 'Steak', 150, 21, 1, 6, 1, 330, 0, 2.5),
        ('protein', 'Barbacoa', 170, 24, 2, 7, 1, 530, 0, 2.5),
        ('protein', 'Carnitas', 210, 23, 0, 12, 0, 450, 0, 7),
        ('protein', 'Sofritas', 150, 8, 9, 10, 3, 560, 5, 1.5),
        # Toppings
        ('topping', 'Fajita Veggies', 20, 1, 5, 0, 1, 150, 2, 0),
        ('topping', 'Fresh Tomato Salsa', 25, 0, 4, 0, 1, 550, 1, 0),
        ('topping', 'Roasted Chili-Corn Salsa', 80, 3, 16, 1.5, 3, 330, 4, 0),
        ('topping', 'Tomatillo-Green Chili Salsa', 15, 0, 4, 0, 0, 260, 2, 0),
        ('topping', 'Tomatillo-Red Chili Salsa', 30, 0, 4, 0, 1, 500, 0, 0),
        ('topping', 'Cheese', 110, 6, 1, 8, 0, 190, 0, 5),
        ('topping', 'Sour Cream', 110, 2, 2, 9, 0, 30, 2, 7),
        ('topping', 'Romaine Lettuce', 5, 0, 1, 0, 1, 0, 0, 0),
        # Extras
        ('extra', 'Guacamole', 230, 2, 8, 22, 6, 370, 1, 3.5),
        ('extra', 'Queso Blanco', 120, 5, 4, 9, 0, 250, 1, 6),
        # Dressings
        ('dressing', 'Chipotle-Honey Vinaigrette', 220, 1, 18, 16, 1, 850, 12, 2.5),
    ],
    'cava': [
        # Bases (Greens + Grains)
        ('base', 'Brown Rice', 310, 7, 48, 10, 5, 770, 2, 2),
        ('base', 'Saffron Basmati Rice', 290, 5, 54, 7, 2, 770, 1, 1),
        ('base', 'Black Lentils', 270, 18, 37, 7, 15, 520, 3, 1),
        ('base', 'SuperGreens', 35, 3, 6, 0.5, 4, 35, 2, 0),
        ('base', 'Arugula', 20, 2, 3, 0.5, 1, 25, 2, 0),
        ('base', 'Baby Spinach', 20, 3, 3, 0, 2, 70, 0, 0),
        ('base', 'Romaine', 20, 1, 4, 0, 3, 10, 1, 0),
        ('base', 'Power Greens', 30, 2, 4, 0, 2, 35, 1, 0),
        # Proteins (Mains)
        ('protein', 'Grilled Chicken', 250, 28, 3, 13, 1, 670, 0, 3),
        ('protein', 'Braised Lamb', 210, 24, 2, 12, 1, 450, 0, 6),
        ('protein', 'Grilled Steak', 170, 23, 1, 9, 0, 280, 0, 3),
        ('protein', 'Harissa Honey Chicken', 260, 26, 7, 14, 2, 670, 3, 3),
        ('protein', 'Falafel', 350, 6, 24, 26, 5, 810, 3, 2),
        ('protein', 'Spicy Lamb Meatballs', 300, 24, 3, 21, 1, 680, 1, 8),
        ('protein', 'Roasted Vegetables', 100, 3, 14, 4.5, 5, 600, 5, 0.5),
        ('protein', 'White Sweet Potatoes', 180, 3, 35, 4, 4, 490, 9, 0.5),
        # Toppings
        ('topping', 'Shredded Romaine', 5, 0, 1, 0, 0, 0, 0, 0),
        ('topping', 'Pita Crisps', 70, 1, 6, 11, 0, 25, 0, 1.5),
        ('topping', 'Sumac Slaw', 30, 1, 3, 1.5, 1, 170, 1, 0),
        ('topping', 'Tomato + Onion', 20, 0, 2, 1.5, 0, 125, 1, 0),
        ('topping', 'Persian Cucumber', 15, 0, 1, 1, 0, 110, 1, 0),
        ('topping', 'Kalamata Olives', 35, 0, 2, 3, 2, 360, 0, 0.5),
        ('topping', 'Fiery Broccoli', 35, 1, 2, 2.5, 1, 170, 1, 0),
        ('topping', 'Pickled Onions', 20, 0, 5, 0, 0, 0, 4, 0),
        ('topping', 'Salt-Brined Pickles', 5, 0, 0, 0, 0, 180, 0, 0),
        ('topping', 'Crumbled Feta', 35, 3, 0, 2.5, 0, 125, 1, 1.5),
        ('topping', 'Fire-Roasted Corn', 45, 1, 5, 2.5, 1, 105, 2, 0),
        ('topping', 'Avocado', 110, 1, 6, 10, 4, 0, 0, 1.5),
        # Dips & Spreads
        ('dressing', 'Tzatziki', 30, 2, 1, 2.5, 0, 60, 1, 1.5),
        ('dressing', 'Hummus', 50, 2, 4, 2.5, 2, 90, 0, 0),
        ('dressing', 'Roasted Eggplant', 50, 0, 2, 5, 1, 160, 0, 0.5),
        ('dressing', 'Crazy Feta', 70, 4, 1, 6, 0, 230, 0, 3),
        ('dressing', 'Harissa', 70, 1, 5, 6, 1, 250, 2, 1),
        ('dressing', 'Red Pepper Hummus', 40, 2, 5, 1.5, 2, 105, 1, 0),
        # Dressings
        ('dressing', 'Balsamic Date Vinaigrette', 60, 0, 7, 4, 1, 250, 5, 0.5),
        ('dressing', 'Yogurt Dill', 30, 2, 1, 2, 0, 190, 0, 1),
        ('dressing', 'Lemon Herb Tahini', 70, 2, 4, 6, 2, 140, 0, 1),
        ('dressing', 'Tahini Caesar', 90, 2, 3, 8, 1, 250, 0, 1),
        ('dressing', 'Greek Vinaigrette', 130, 0, 1, 14, 0, 230, 0, 2),
        ('dressing', 'Skhug', 80, 0, 1, 9, 0, 150, 0, 1),
        ('dressing', 'Hot Harissa Vinaigrette', 70, 0, 1, 7, 0, 270, 1, 1),
        ('dressing', 'Garlic Dressing', 180, 0, 0, 20, 0, 90, 0, 1.5),
        # Sides (as base option)
        ('base', 'Whole Pita', 320, 13, 54, 6, 6, 700, 3, 1),
        ('base', 'Side Pita', 80, 3, 14, 1.5, 2, 180, 1, 0),
    ],
    'sweetgreen': [
        # Bases
        ('base', 'Arugula', 15, 2, 2, 0, 1, 15, 1, 0),
        ('base', 'Baby Spinach', 15, 1, 2, 0, 1, 40, 0, 0),
        ('base', 'Chopped Romaine', 25, 1, 3, 0, 2, 10, 1, 0),
        ('base', 'Golden Quinoa', 110, 4, 16, 3, 2, 370, 0, 0),
        ('base', 'Shredded Kale', 35, 3, 6, 1, 3, 25, 2, 0),
        ('base', 'Spring Mix', 15, 0, 0, 0, 0, 0, 0, 0),
        ('base', 'White Rice', 120, 2, 27, 1, 1, 130, 0, 0),
        ('base', 'Wild Rice', 155, 3, 31, 2, 2, 150, 0, 0),
        ('base', 'Bread', 80, 3, 18, 0, 3, 200, 1, 0),
        # Toppings
        ('topping', 'Apples', 20, 0, 4, 0, 1, 0, 3, 0),
        ('topping', 'Charred Balsamic Cabbage', 35, 1, 5, 2, 1, 140, 3, 0),
        ('topping', 'Chickpeas', 45, 2, 7, 1, 2, 250, 1, 0),
        ('topping', 'Cilantro', 0, 0, 0, 0, 0, 0, 0, 0),
        ('topping', 'Crispy Onions', 40, 0, 3, 3, 0, 30, 0, 0),
        ('topping', 'Crispy Rice', 80, 2, 14, 2, 0, 280, 0, 0),
        ('topping', 'Cucumbers', 5, 0, 1, 0, 0, 0, 0, 0),
        ('topping', 'Garlic Breadcrumbs', 50, 1, 6, 3, 0, 180, 1, 0),
        ('topping', 'Pickled Onions', 20, 0, 5, 0, 0, 260, 4, 0),
        ('topping', 'Raw Carrots', 10, 0, 2, 0, 1, 15, 1, 0),
        ('topping', 'Roasted Almonds', 80, 3, 3, 6, 2, 0, 1, 0),
        ('topping', 'Roasted Sweet Potatoes', 60, 1, 11, 1, 2, 290, 2, 0),
        ('topping', 'Shredded Cabbage', 10, 0, 2, 0, 1, 5, 1, 0),
        ('topping', 'Spicy Broccoli', 30, 1, 2, 3, 1, 125, 0, 0),
        ('topping', 'Tomatoes', 10, 1, 2, 0, 1, 10, 1, 0),
        ('topping', 'Tortilla Chips', 80, 1, 10, 4, 1, 10, 0, 0),
        # Premiums
        ('topping', 'Crumbled Bacon', 70, 9, 0, 5, 0, 630, 0, 0),
        ('topping', 'Goat Cheese', 90, 7, 2, 7, 0, 160, 0, 0),
        ('topping', 'Hard Boiled Egg', 70, 7, 1, 5, 0, 190, 0, 0),
        ('topping', 'Parmesan Crisps', 100, 6, 1, 8, 0, 480, 0, 0),
        # Super Premium Proteins
        ('protein', 'Avocado', 160, 3, 8, 13, 9, 0, 0, 0),
        ('protein', 'Blackened Chicken', 150, 20, 1, 6, 0, 410, 0, 0),
        ('protein', 'Caramelized Garlic Steak', 220, 25, 2, 13, 0, 650, 0, 4),
        ('protein', 'Miso Glazed Salmon', 240, 23, 2, 15, 0, 140, 1, 0),
        ('protein', 'Roasted Chicken', 110, 23, 0, 3, 0, 350, 0, 0),
        ('protein', 'Roasted Tofu', 130, 9, 3, 10, 2, 340, 0, 0),
        ('protein', 'Warm Portobello Mix', 60, 1, 3, 6, 1, 340, 1, 0),
        # Dressings
        ('dressing', 'Apple Vinaigrette', 130, 0, 4, 13, 0, 150, 2, 0),
        ('dressing', 'Balsamic Vinaigrette', 210, 0, 5, 22, 0, 290, 4, 0),
        ('dressing', 'Caesar', 160, 1, 1, 17, 0, 350, 0, 0),
        ('dressing', 'Green Goddess Ranch', 180, 1, 1, 19, 0, 350, 0, 0),
        ('dressing', 'Honey BBQ Sauce', 55, 0, 6, 0, 0, 320, 12, 0),
        ('dressing', 'Hot Honey Mustard Sauce', 170, 0, 9, 14, 0, 350, 9, 0),
        ('dressing', 'Lime Cilantro Jalapeno Sauce', 140, 0, 2, 15, 0, 380, 0, 0),
        ('dressing', 'Pesto Vinaigrette', 110, 0, 0, 9, 0, 160, 0, 0),
        ('dressing', 'Sweetgreen Hot Sauce', 10, 1, 2, 0, 1, 170, 1, 0),
        ('dressing', 'Spicy Cashew', 170, 3, 4, 15, 1, 370, 4, 0),
        ('dressing', 'Miso Sesame Ginger', 190, 1, 2, 20, 0, 390, 2, 0),
    ],
    'dig-inn': [
        # Bases (Sides)
        ('base', 'Classic Brown Rice', 210, 4, 41, 10, 3, 430, 0, 0),
        ('base', 'Spiced Farro', 240, 6, 39, 8, 4, 370, 2, 1),
        ('base', 'Farm Greens with Mint', 10, 0, 2, 0, 0, 10, 1, 0),
        ('base', 'Cashew Kale Caesar', 140, 4, 8, 14, 2, 360, 1, 1.5),
        # Proteins (Mains)
        ('protein', 'Charred Chicken', 230, 28, 1, 12, 0, 740, 0, 3),
        ('protein', 'Herb Roasted Chicken', 170, 24, 0, 8, 0, 420, 0, 2),
        ('protein', 'Crispy Chicken', 320, 24, 20, 15, 0, 840, 2, 2),
        ('protein', 'Hot Honey Chicken', 280, 28, 13, 12, 0, 910, 11, 3),
        ('protein', 'Seared Wild Salmon', 270, 23, 1, 19, 0, 770, 0, 2.5),
        ('protein', 'Crispy Tofu', 280, 19, 8, 20, 0, 770, 0, 1.5),
        # Toppings (Sides)
        ('topping', 'Tomatoes & Cucumbers', 25, 0, 6, 0, 1, 85, 5, 0),
        ('topping', 'Marinated Cannellini Beans', 160, 5, 17, 8, 6, 520, 4, 0),
        ('topping', 'Charred Broccoli with Lemon', 100, 3, 9, 7, 3, 420, 2, 0),
        ('topping', 'Sheet Tray Carrots', 80, 1, 11, 6, 3, 350, 5, 0),
        ('topping', 'Roasted Sweet Potatoes', 260, 3, 43, 6, 6, 220, 9, 0),
        ('topping', 'Chili Lime Brussels Sprouts', 130, 3, 14, 8, 4, 630, 11, 0),
        # Extras
        ('extra', 'Avocado with Olive Oil', 140, 1, 6, 13, 5, 115, 0, 2),
        ('extra', 'Focaccia', 270, 7, 43, 8, 2, 600, 2, 1),
        # Sauces/Dressings
        ('dressing', 'Garlic Aioli', 80, 0, 0, 8, 0, 100, 0, 0),
        ('dressing', 'Hot Honey', 50, 0, 12, 0, 0, 170, 11, 0),
        ('dressing', 'Pesto', 130, 0, 0, 14, 0, 120, 0, 1.5),
        ('dressing', 'Sriracha', 20, 0, 3, 0, 0, 440, 2, 0),
        ('dressing', 'Balsamic Vinaigrette', 110, 0, 3, 11, 0, 240, 2, 0),
        ('dressing', 'Tarragon Mustard', 100, 0, 1, 11, 0, 360, 1, 1),
    ],
    'naya': [
        # Bases
        ('base', 'Romaine Lettuce', 15, 1, 3, 0, 2, 10, 1, 0),
        ('base', 'Seasonal Greens', 35, 4, 6, 0.5, 3, 180, 1, 0),
        ('base', 'Brown Rice with Lentils', 450, 11, 94, 19, 7, 490, 0, 2),
        ('base', 'Vermicelli Rice', 150, 5, 41, 5, 0, 210, 0, 2.5),
        ('base', 'White Pita', 300, 10, 60, 2.5, 2, 530, 4, 0),
        ('base', 'Whole Wheat Pita', 230, 13, 40, 4, 7, 370, 3, 0),
        # Proteins
        ('protein', 'Chicken Shawarma', 190, 23, 1, 11, 0, 280, 0, 2.5),
        ('protein', 'Chicken Kebab', 150, 20, 2, 7, 0, 410, 0, 0),
        ('protein', 'Beef Shawarma', 250, 31, 2, 15, 0, 430, 1, 3),
        ('protein', 'Braised Beef', 270, 20, 11, 17, 3, 690, 5, 9),
        ('protein', 'Kafta Lamb Kebab', 270, 18, 2, 20, 0, 530, 0, 8),
        ('protein', 'Falafel (5 pcs)', 220, 12, 40, 11, 22, 590, 0, 0.5),
        ('protein', 'Cauliflower', 120, 2, 5, 11, 3, 40, 2, 1.5),
        # Toppings
        ('topping', 'Baba Ghannouj', 70, 2, 11, 4.5, 2, 280, 2, 1),
        ('topping', 'Feta Cheese', 70, 4, 1, 6, 0, 260, 1, 4),
        ('topping', 'Cucumbers', 5, 0, 1, 0, 0, 0, 0, 0),
        ('topping', 'Cabbage Slaw', 60, 0, 2, 6, 0, 140, 0, 1),
        ('topping', 'Hummus', 230, 5, 10, 20, 3, 270, 0, 2.5),
        ('topping', 'Jalapeños', 0, 0, 0, 0, 0, 0, 0, 0),
        ('topping', 'Kalamata Olives', 30, 0, 0, 3, 0, 90, 0, 0),
        ('topping', 'Sumac Onions', 15, 0, 3, 0, 0, 20, 1, 0),
        ('topping', 'Lebanese Pickles', 5, 0, 2, 0, 0, 610, 0, 0),
        ('topping', 'Pickled Turnips', 5, 0, 1, 0, 0, 470, 1, 0),
        ('topping', 'Tomatoes', 10, 0, 2, 0, 0, 0, 1, 0),
        ('topping', 'Romaine Lettuce', 5, 0, 1, 0, 0, 10, 0, 0),
        # Sauces/Dressings
        ('dressing', 'Toum (Garlic Whip)', 80, 0, 0, 8, 0, 70, 0, 0.5),
        ('dressing', 'Cucumber Yogurt', 35, 1, 1, 3, 1, 50, 1, 2),
        ('dressing', 'Lemon Tahini', 70, 2, 3, 6, 0, 70, 0, 1),
        ('dressing', 'Spicy Red Pepper Sauce', 45, 0, 2, 4, 0, 260, 0, 0),
        ('dressing', 'Zesty Jalapeño Sauce', 110, 0, 1, 11, 0, 95, 0, 1),
        ('dressing', 'Pomegranate Vinaigrette', 80, 0, 13, 3, 0, 290, 6, 2),
        ('dressing', 'Red Pepper Hummus', 180, 6, 12, 12, 3, 420, 3, 3),
        ('dressing', 'Pita Crunch', 70, 1, 8, 3, 0, 100, 0, 0.5),
    ],
    'sweetfin': [
        # Bases (Large serving)
        ('base', 'Bamboo Rice', 290, 5, 65, 0, 0, 0, 0, 0),
        ('base', 'Cauliflower Rice', 120, 4, 9, 9, 5, 960, 4, 0.5),
        ('base', 'Citrus Kale Salad', 60, 2, 6, 3.5, 2, 320, 2, 0),
        ('base', 'Forbidden Rice', 340, 10, 73, 3, 4, 0, 2, 0),
        ('base', 'Kelp Noodle Slaw', 140, 2, 10, 10, 2, 750, 4, 1.5),
        # Proteins (Large serving — fixed: fat column was reading "cal from fat" before)
        ('protein', 'Albacore Tuna', 120, 28, 0, 0.5, 0, 50, 0, 0),
        ('protein', 'Yellowfin Tuna', 120, 28, 0, 0.5, 0, 50, 0, 0),
        ('protein', 'Salmon', 240, 23, 0, 15, 0, 65, 0, 3.5),
        ('protein', 'Shrimp', 130, 26, 2, 2, 0, 470, 0, 0.5),
        ('protein', 'Tofu', 110, 10, 4, 6, 2, 210, 1, 0),
        ('protein', 'Chicken', 120, 27, 0, 1.5, 0, 290, 0, 0),
        ('protein', 'Vegetable Poke', 180, 6, 24, 8, 9, 55, 6, 1),
        # Sauces (Large serving where applicable)
        ('dressing', 'Black Garlic Gochujang', 150, 1, 7, 14, 1, 400, 5, 2),
        ('dressing', 'Spicy Mayo', 130, 1, 2, 14, 0, 830, 1, 2.5),
        ('dressing', 'Miso Sesame Shoyu', 100, 0, 3, 9, 0, 370, 3, 1.5),
        ('dressing', 'Ponzu Lime', 35, 0, 6, 0, 0, 630, 6, 0),
        ('dressing', 'Sriracha Ponzu', 60, 1, 4, 4, 0, 620, 3, 0.5),
        ('dressing', 'Yuzu Kosho', 60, 1, 2, 5, 0, 610, 2, 0),
        ('dressing', 'Cilantro Lime Jalapeno Vinaigrette', 130, 0, 2, 14, 0, 125, 0, 2),
        ('dressing', 'Sesame Mayo', 150, 0, 1, 15, 0, 580, 1, 2.5),
        ('dressing', 'Garlic Lemongrass Ponzu', 40, 0, 7, 0, 0, 590, 6, 0),
        # Fruits & Veggies (Large serving)
        ('topping', 'Edamame', 30, 4, 3, 0.5, 3, 10, 0, 0),
        ('topping', 'Japanese Eggplant', 80, 0, 5, 7, 1, 140, 2, 1),
        ('topping', 'Chile Marinated Oranges', 30, 1, 7, 0, 2, 0, 5, 0),
        ('topping', 'Rapini', 40, 1, 1, 4, 1, 95, 0, 0.5),
        ('topping', 'Shimeji Mushrooms', 30, 1, 1, 2.5, 0, 50, 0, 0),
        ('topping', 'Mango', 20, 0, 5, 0, 0, 0, 4, 0),
        ('topping', 'Seaweed Salad', 15, 0, 2, 1, 1, 135, 1, 0),
        ('topping', 'Pineapple', 10, 0, 3, 0, 0, 0, 2, 0),
        ('topping', 'Jicama', 10, 0, 2, 0, 1, 0, 0, 0),
        ('topping', 'Shaved Red Onion', 10, 0, 2, 0, 0, 0, 1, 0),
        ('topping', 'Cucumber', 0, 0, 0, 0, 0, 0, 0, 0),
        ('topping', 'Pickled Ginger', 5, 0, 1, 0, 0, 210, 0, 0),
        ('topping', 'Napa Cabbage', 5, 0, 1, 0, 0, 0, 0, 0),
        ('topping', 'Sundried Tomatoes', 5, 0, 1, 0, 0, 0, 1, 0),
        ('topping', 'Carrots', 5, 0, 1, 0, 0, 10, 1, 0),
        ('topping', 'Bean Sprouts', 5, 0, 1, 0, 0, 0, 1, 0),
        # Crunchy Add-Ons
        ('topping', 'Crispy Onion', 35, 0, 2, 2.5, 0, 0, 1, 0),
        ('topping', 'Crispy Garlic', 30, 1, 4, 1.5, 0, 0, 0, 0),
        ('topping', 'Wasabi Peas', 30, 1, 5, 1, 0, 25, 1, 0),
        ('topping', 'Wasabi Toasted Coconut', 30, 0, 3, 1.5, 0, 65, 2, 1.5),
        ('topping', 'Wasabi Furikake', 25, 0, 3, 1, 0, 105, 1, 0),
        # Premium Add-Ons
        ('extra', 'Cashews', 100, 3, 6, 8, 1, 0, 0, 1.5),
        ('extra', 'Almonds', 80, 3, 3, 7, 2, 0, 0, 0.5),
        ('extra', 'Avocado', 80, 1, 4, 7, 3, 0, 0, 1),
        ('extra', 'Macadamia Nuts', 60, 1, 1, 6, 1, 0, 0, 1),
        ('extra', 'White Truffle Oil', 45, 0, 0, 5, 0, 0, 0, 0.5),
        ('extra', 'Asparagus', 35, 1, 1, 3.5, 0, 70, 0, 0),
        ('extra', 'Wasabi Tobiko', 15, 2, 2, 0, 0, 135, 2, 0),
        ('extra', 'Kimchee', 10, 0, 2, 0, 1, 220, 0, 0),
        ('extra', 'Pickled Shiitakes', 10, 1, 2, 0, 1, 80, 1, 0),
        ('extra', 'Blistered Shishito', 10, 0, 2, 0, 1, 0, 1, 0),
        # Herbs & Spices
        ('topping', 'Chile Oil', 130, 0, 0, 14, 0, 0, 0, 3),
        ('topping', 'Wasabi Drizzle', 25, 0, 1, 2.5, 0, 45, 0, 0),
        ('topping', 'Sliced Jalapenos', 10, 0, 2, 0, 1, 0, 1, 0),
        ('topping', 'Shiso', 10, 1, 2, 0, 1, 0, 0, 0),
        ('topping', 'Cilantro', 5, 0, 1, 0, 0, 5, 0, 0),
        ('topping', 'Pickled Fresno', 5, 0, 1, 0, 0, 25, 1, 0),
        ('topping', 'Hijiki', 5, 0, 1, 0, 1, 15, 0, 0),
        ('topping', 'Daikon Sprouts', 5, 1, 1, 0, 0, 0, 0, 0),
    ],
    'mod-pizza': [
        # Note: MOD is build-your-own pizza — different structure
        # Using their individual toppings isn't in the PDF as cleanly
        # We'll skip MOD for now since their PDF is HTML-based
    ],
}

# Format: (category, name, calories, protein, carbs, fat, fiber, sodium, sugar, saturated_fat)


class Command(BaseCommand):
    help = 'Import BYO component nutrition data'

    def handle(self, *args, **options):
        from api.models import Restaurant, ByoComponent

        total_created = 0
        total_skipped = 0

        for slug, components in BYO_DATA.items():
            if not components:
                self.stdout.write(f'  Skipping {slug} (no data)')
                continue

            try:
                restaurant = Restaurant.objects.get(slug=slug)
            except Restaurant.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  Restaurant "{slug}" not found, skipping'))
                continue

            self.stdout.write(f'\n{restaurant.name} ({slug}):')

            if not restaurant.has_byo:
                restaurant.has_byo = True
                restaurant.save(update_fields=['has_byo'])
                self.stdout.write(f'  Enabled has_byo flag')

            for i, comp in enumerate(components):
                category, name, calories, protein, carbs, fat, fiber, sodium, sugar, saturated_fat = comp

                _, created = ByoComponent.objects.update_or_create(
                    restaurant=restaurant,
                    name=name,
                    defaults={
                        'category': category,
                        'calories': calories,
                        'protein': protein,
                        'carbs': carbs,
                        'fat': fat,
                        'fiber': fiber,
                        'sodium': sodium,
                        'sugar': sugar,
                        'saturated_fat': saturated_fat,
                        'sort_order': i,
                        'is_available': True,
                    }
                )
                if created:
                    total_created += 1
                else:
                    total_skipped += 1
                self.stdout.write(f'  {"+" if created else "="} [{category}] {name} ({calories} cal, {protein}g protein)')

        self.stdout.write(self.style.SUCCESS(
            f'\nDone! Created: {total_created}, Updated: {total_skipped}'
        ))
