import streamlit as st
import pandas as pd
from datetime import datetime
from geopy.distance import geodesic
import os

st.set_page_config(
    page_title="INDE - Wholesale Delivery Platform",
    page_icon="🚚",
    layout="wide"
)

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
if ADMIN_PASSWORD is None:
    st.error("⚠️ ADMIN_PASSWORD environment variable is not set. Please configure it in Replit Secrets.")
    st.stop()

if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

if 'products' not in st.session_state:
    st.session_state.products = [
        {
            'id': 1,
            'name': 'Organic Tea Plants (50 saplings)',
            'category': 'Plants',
            'price': 5000,
            'weight_kg': 25,
            'volume_m3': 2.0,
            'min_quantity': 50,
            'unit': 'saplings',
            'supplier': 'Assam Tea Nursery',
            'location': 'Guwahati',
            'coordinates': (26.1445, 91.7362),
            'description': 'Premium Assam tea saplings, ready for plantation',
            'stock': 500
        },
        {
            'id': 2,
            'name': 'Teak Wood Furniture Set',
            'category': 'Furniture',
            'price': 45000,
            'weight_kg': 150,
            'volume_m3': 8.0,
            'min_quantity': 1,
            'unit': 'set',
            'supplier': 'Jorhat Woodworks',
            'location': 'Jorhat',
            'coordinates': (26.7509, 94.2037),
            'description': 'Complete office furniture set - 4 tables, 8 chairs',
            'stock': 20
        },
        {
            'id': 3,
            'name': 'Organic Fertilizer (50kg bags)',
            'category': 'Fertilizers',
            'price': 800,
            'weight_kg': 50,
            'volume_m3': 0.5,
            'min_quantity': 10,
            'unit': 'bags',
            'supplier': 'Green Farm Supplies',
            'location': 'Dibrugarh',
            'coordinates': (27.4728, 94.9120),
            'description': 'Premium organic compost for all crops',
            'stock': 1000
        },
        {
            'id': 4,
            'name': 'Cement (50kg bags)',
            'category': 'Building Materials',
            'price': 350,
            'weight_kg': 50,
            'volume_m3': 0.4,
            'min_quantity': 50,
            'unit': 'bags',
            'supplier': 'Assam Cement Co.',
            'location': 'Silchar',
            'coordinates': (24.8333, 92.7789),
            'description': 'High-grade cement for construction projects',
            'stock': 5000
        },
        {
            'id': 5,
            'name': 'Steel Rods (12mm x 12m)',
            'category': 'Building Materials',
            'price': 550,
            'weight_kg': 10.6,
            'volume_m3': 0.1,
            'min_quantity': 100,
            'unit': 'rods',
            'supplier': 'Tezpur Steel',
            'location': 'Tezpur',
            'coordinates': (26.6338, 92.8000),
            'description': 'TMT steel rods for construction',
            'stock': 2000
        },
        {
            'id': 6,
            'name': 'Bamboo Plants (10ft height)',
            'category': 'Plants',
            'price': 200,
            'weight_kg': 15,
            'volume_m3': 1.5,
            'min_quantity': 20,
            'unit': 'plants',
            'supplier': 'Bamboo Growers Assam',
            'location': 'Nagaon',
            'coordinates': (26.3467, 92.6833),
            'description': 'Mature bamboo plants for landscaping and construction',
            'stock': 300
        },
        {
            'id': 7,
            'name': 'Thermocol Carton Boxes',
            'category': 'Building Materials',
            'price': 50,
            'weight_kg': 0.5,
            'volume_m3': 0.15,
            'min_quantity': 20,
            'unit': 'boxes',
            'supplier': 'Packaging Solutions',
            'location': 'Barpeta Road',
            'coordinates': (26.5005, 90.9664),
            'description': 'Lightweight thermocol boxes for packaging and insulation',
            'stock': 500
        }
    ]

if 'orders' not in st.session_state:
    st.session_state.orders = []

if 'drivers' not in st.session_state:
    st.session_state.drivers = [
        {
            'id': 1,
            'name': 'Raju Kumar',
            'phone': '9876543210',
            'vehicle_type': 'Mini Truck (1 Ton)',
            'capacity_kg': 1000,
            'capacity_m3': 10,
            'location': 'Guwahati',
            'coordinates': (26.1445, 91.7362),
            'available': True
        },
        {
            'id': 2,
            'name': 'Sanjay Sharma',
            'phone': '9876543211',
            'vehicle_type': 'Large Truck (5 Ton)',
            'capacity_kg': 5000,
            'capacity_m3': 30,
            'location': 'Jorhat',
            'coordinates': (26.7509, 94.2037),
            'available': True
        }
    ]

if 'selected_driver_id' not in st.session_state:
    st.session_state.selected_driver_id = None

ASSAM_CITIES = {
    'Guwahati': (26.1445, 91.7362),
    'Jorhat': (26.7509, 94.2037),
    'Dibrugarh': (27.4728, 94.9120),
    'Silchar': (24.8333, 92.7789),
    'Tezpur': (26.6338, 92.8000),
    'Nagaon': (26.3467, 92.6833),
    'Bongaigaon': (26.4833, 90.5667),
    'Diphu': (25.8417, 93.4314),
    'Goalpara': (26.1667, 90.6167),
    'Sivasagar': (26.9847, 94.6378),
    'Barpeta Road': (26.5005, 90.9664),
    'Howly': (26.4232, 90.9801)
}

def calculate_distance(from_coords, to_coords):
    return geodesic(from_coords, to_coords).kilometers

def calculate_delivery_price(weight_kg, volume_m3, quantity, distance_km):
    base_rate_per_km = 15
    weight_factor = weight_kg * quantity * 0.5
    volume_factor = volume_m3 * quantity * 100
    distance_charge = distance_km * base_rate_per_km
    
    total_delivery = distance_charge + weight_factor + volume_factor
    
    if distance_km > 100:
        total_delivery *= 1.2
    
    return round(total_delivery, 2)

def calculate_total_price(product, quantity, delivery_location):
    product_total = product['price'] * quantity
    
    delivery_coords = ASSAM_CITIES.get(delivery_location, (26.1445, 91.7362))
    distance = calculate_distance(product['coordinates'], delivery_coords)
    
    delivery_charge = calculate_delivery_price(
        product['weight_kg'],
        product['volume_m3'],
        quantity,
        distance
    )
    
    return {
        'product_total': product_total,
        'delivery_charge': delivery_charge,
        'distance_km': round(distance, 2),
        'grand_total': product_total + delivery_charge
    }

st.sidebar.title("🚚 INDE")
st.sidebar.markdown("### Wholesale Delivery Platform")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["🏠 Browse Products", "🛒 Place Order", "🚛 Driver Dashboard", "👤 Admin Panel"]
)

if page == "🏠 Browse Products":
    st.title("🏠 INDE - Browse Wholesale Products")
    st.markdown("### Convenient bulk ordering for shops, markets, and builders across Assam")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        category_filter = st.selectbox(
            "Filter by Category",
            ["All"] + sorted(list(set([p['category'] for p in st.session_state.products])))
        )
    with col2:
        location_filter = st.selectbox(
            "Filter by Location",
            ["All"] + sorted(list(set([p['location'] for p in st.session_state.products])))
        )
    with col3:
        search_query = st.text_input("Search Products", "")
    
    filtered_products = st.session_state.products
    
    if category_filter != "All":
        filtered_products = [p for p in filtered_products if p['category'] == category_filter]
    
    if location_filter != "All":
        filtered_products = [p for p in filtered_products if p['location'] == location_filter]
    
    if search_query:
        filtered_products = [p for p in filtered_products if search_query.lower() in p['name'].lower() or search_query.lower() in p['description'].lower()]
    
    st.markdown(f"### Showing {len(filtered_products)} Products")
    
    for product in filtered_products:
        with st.expander(f"**{product['name']}** - ₹{product['price']:,} per {product['unit']}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Category:** {product['category']}")
                st.markdown(f"**Description:** {product['description']}")
                st.markdown(f"**Supplier:** {product['supplier']}")
                st.markdown(f"**Location:** {product['location']}")
                st.markdown(f"**Minimum Order:** {product['min_quantity']} {product['unit']}")
                st.markdown(f"**Available Stock:** {product['stock']} {product['unit']}")
            
            with col2:
                st.markdown(f"**Specifications:**")
                st.markdown(f"- Weight: {product['weight_kg']} kg per {product['unit']}")
                st.markdown(f"- Volume: {product['volume_m3']} m³ per {product['unit']}")
                st.markdown(f"- Price: ₹{product['price']:,}")

elif page == "🛒 Place Order":
    st.title("🛒 Place Your Order")
    st.markdown("### Select products and get instant delivery pricing")
    
    if len(st.session_state.products) == 0:
        st.warning("No products available. Please add products first.")
    else:
        product_names = [f"{p['name']} (₹{p['price']:,})" for p in st.session_state.products]
        selected_product_idx = st.selectbox("Select Product", range(len(product_names)), format_func=lambda x: product_names[x])
        selected_product = st.session_state.products[selected_product_idx]
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Product Details:**")
            st.info(f"""
            **{selected_product['name']}**
            
            Category: {selected_product['category']}
            Supplier: {selected_product['supplier']}
            Location: {selected_product['location']}
            
            Base Price: ₹{selected_product['price']:,} per {selected_product['unit']}
            Minimum Order: {selected_product['min_quantity']} {selected_product['unit']}
            Stock Available: {selected_product['stock']} {selected_product['unit']}
            """)
        
        with col2:
            st.markdown("**Order Details:**")
            buyer_name = st.text_input("Your Name/Business Name")
            buyer_phone = st.text_input("Contact Number")
            quantity = st.number_input(
                f"Quantity ({selected_product['unit']})",
                min_value=selected_product['min_quantity'],
                max_value=selected_product['stock'],
                value=selected_product['min_quantity'],
                step=selected_product['min_quantity']
            )
            delivery_location = st.selectbox("Delivery Location", sorted(ASSAM_CITIES.keys()))
            delivery_address = st.text_area("Full Delivery Address")
        
        if quantity < selected_product['min_quantity']:
            st.error(f"Minimum order quantity is {selected_product['min_quantity']} {selected_product['unit']}")
        else:
            pricing = calculate_total_price(selected_product, quantity, delivery_location)
            
            st.markdown("---")
            st.markdown("### 💰 Price Breakdown")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Product Cost", f"₹{pricing['product_total']:,.2f}")
            with col2:
                st.metric("Delivery Charge", f"₹{pricing['delivery_charge']:,.2f}")
            with col3:
                st.metric("Distance", f"{pricing['distance_km']} km")
            with col4:
                st.metric("**TOTAL**", f"₹{pricing['grand_total']:,.2f}")
            
            st.info(f"💡 Delivery fee calculated based on: Weight ({selected_product['weight_kg']} kg × {quantity}), Volume ({selected_product['volume_m3']} m³ × {quantity}), and Distance ({pricing['distance_km']} km)")
            
            st.markdown("---")
            
            if st.button("🚀 Place Order", type="primary"):
                if not buyer_name or not buyer_phone or not delivery_address:
                    st.error("Please fill in all buyer details")
                else:
                    order = {
                        'id': len(st.session_state.orders) + 1,
                        'product_id': selected_product['id'],
                        'product_name': selected_product['name'],
                        'buyer_name': buyer_name,
                        'buyer_phone': buyer_phone,
                        'quantity': quantity,
                        'delivery_location': delivery_location,
                        'delivery_address': delivery_address,
                        'pickup_location': selected_product['location'],
                        'product_total': pricing['product_total'],
                        'delivery_charge': pricing['delivery_charge'],
                        'grand_total': pricing['grand_total'],
                        'distance_km': pricing['distance_km'],
                        'status': 'Order Placed',
                        'driver_id': None,
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'weight_kg': selected_product['weight_kg'] * quantity,
                        'volume_m3': selected_product['volume_m3'] * quantity
                    }
                    st.session_state.orders.append(order)
                    
                    for p in st.session_state.products:
                        if p['id'] == selected_product['id']:
                            p['stock'] -= quantity
                    
                    st.success(f"✅ Order #{order['id']} placed successfully! Total: ₹{pricing['grand_total']:,.2f}")
                    st.balloons()
                    st.info("Your order has been sent to available drivers. You will be contacted soon!")

elif page == "🚛 Driver Dashboard":
    st.title("🚛 Driver Dashboard")
    st.markdown("### Manage your deliveries and earnings")
    
    if len(st.session_state.drivers) > 0:
        driver_options = {f"{d['name']} ({d['vehicle_type']})": d['id'] for d in st.session_state.drivers}
        selected_driver_name = st.selectbox(
            "👤 Select Your Driver Account",
            options=list(driver_options.keys()),
            index=0 if st.session_state.selected_driver_id is None else list(driver_options.values()).index(st.session_state.selected_driver_id) if st.session_state.selected_driver_id in driver_options.values() else 0
        )
        st.session_state.selected_driver_id = driver_options[selected_driver_name]
        
        selected_driver = next(d for d in st.session_state.drivers if d['id'] == st.session_state.selected_driver_id)
        st.info(f"📱 Logged in as: **{selected_driver['name']}** | Vehicle: {selected_driver['vehicle_type']} | Location: {selected_driver['location']}")
    
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["📋 Available Jobs", "➕ Register as Driver"])
    
    with tab1:
        if st.session_state.selected_driver_id is None:
            st.warning("⚠️ Please register as a driver first in the 'Register as Driver' tab to view available jobs.")
        else:
            st.markdown("### Available Delivery Jobs")
            
            available_orders = [o for o in st.session_state.orders if o['status'] == 'Order Placed']
            
            if len(available_orders) == 0:
                st.info("No delivery jobs available at the moment. Check back later!")
            else:
                for order in available_orders:
                    with st.expander(f"Order #{order['id']} - {order['product_name']} | ₹{order['delivery_charge']:,.2f} delivery fee"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown("**📦 Load Details:**")
                            st.write(f"Product: {order['product_name']}")
                            st.write(f"Quantity: {order['quantity']}")
                            st.write(f"Weight: {order['weight_kg']} kg")
                            st.write(f"Volume: {order['volume_m3']} m³")
                        
                        with col2:
                            st.markdown("**📍 Route:**")
                            st.write(f"Pickup: {order['pickup_location']}")
                            st.write(f"Delivery: {order['delivery_location']}")
                            st.write(f"Distance: {order['distance_km']} km")
                            st.write(f"Address: {order['delivery_address']}")
                        
                        with col3:
                            st.markdown("**💰 Earnings:**")
                            st.write(f"Delivery Fee: ₹{order['delivery_charge']:,.2f}")
                            st.write(f"Buyer: {order['buyer_name']}")
                            st.write(f"Contact: {order['buyer_phone']}")
                        
                        if st.button(f"Accept Job #{order['id']}", key=f"accept_{order['id']}"):
                            order['status'] = 'Driver Assigned'
                            order['driver_id'] = st.session_state.selected_driver_id
                            st.success(f"✅ Job #{order['id']} accepted! Contact buyer to coordinate pickup.")
                            st.rerun()
            
            st.markdown("---")
            st.markdown("### My Active Deliveries")
            
            my_deliveries = [o for o in st.session_state.orders if o.get('driver_id') == st.session_state.selected_driver_id and o['status'] != 'Delivered']
            
            if len(my_deliveries) == 0:
                st.info("You have no active deliveries.")
            else:
                for delivery in my_deliveries:
                    with st.expander(f"Order #{delivery['id']} - {delivery['status']}"):
                        st.write(f"**Product:** {delivery['product_name']}")
                        st.write(f"**Route:** {delivery['pickup_location']} → {delivery['delivery_location']}")
                        st.write(f"**Buyer:** {delivery['buyer_name']} ({delivery['buyer_phone']})")
                        
                        new_status = st.selectbox(
                            "Update Status",
                            ["Driver Assigned", "Picked Up", "In Transit", "Delivered"],
                            index=["Driver Assigned", "Picked Up", "In Transit", "Delivered"].index(delivery['status']),
                            key=f"status_{delivery['id']}"
                        )
                        
                        if st.button(f"Update Status for Order #{delivery['id']}", key=f"update_{delivery['id']}"):
                            delivery['status'] = new_status
                            st.success(f"Status updated to: {new_status}")
                            st.rerun()
    
    with tab2:
        st.markdown("### Register as a Driver")
        
        with st.form("driver_registration"):
            driver_name = st.text_input("Full Name *")
            driver_phone = st.text_input("Contact Number *")
            vehicle_type = st.selectbox(
                "Vehicle Type *",
                ["Mini Truck (1 Ton)", "Medium Truck (3 Ton)", "Large Truck (5 Ton)", "Extra Large Truck (10 Ton)"]
            )
            
            capacity_map = {
                "Mini Truck (1 Ton)": (1000, 10),
                "Medium Truck (3 Ton)": (3000, 20),
                "Large Truck (5 Ton)": (5000, 30),
                "Extra Large Truck (10 Ton)": (10000, 50)
            }
            
            driver_location = st.selectbox("Operating Location *", sorted(ASSAM_CITIES.keys()))
            
            submitted = st.form_submit_button("Register", type="primary")
            
            if submitted:
                if not driver_name or not driver_phone:
                    st.error("Please fill in all required fields")
                else:
                    capacity_kg, capacity_m3 = capacity_map[vehicle_type]
                    
                    new_driver = {
                        'id': max([d['id'] for d in st.session_state.drivers], default=0) + 1,
                        'name': driver_name,
                        'phone': driver_phone,
                        'vehicle_type': vehicle_type,
                        'capacity_kg': capacity_kg,
                        'capacity_m3': capacity_m3,
                        'location': driver_location,
                        'coordinates': ASSAM_CITIES[driver_location],
                        'available': True
                    }
                    st.session_state.drivers.append(new_driver)
                    st.session_state.selected_driver_id = new_driver['id']
                    st.success(f"✅ Driver registered successfully! Welcome, {driver_name}!")
                    st.balloons()

elif page == "👤 Admin Panel":
    if not st.session_state.admin_logged_in:
        st.title("🔐 Admin Login")
        st.markdown("### Enter admin password to access the control panel")
        
        password = st.text_input("Admin Password", type="password")
        
        if st.button("Login", type="primary"):
            if password == ADMIN_PASSWORD:
                st.session_state.admin_logged_in = True
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("❌ Incorrect password. Please try again.")
    else:
        col1, col2 = st.columns([6, 1])
        with col1:
            st.title("👤 Admin Dashboard")
            st.markdown("### Platform Overview and Management")
        with col2:
            if st.button("Logout"):
                st.session_state.admin_logged_in = False
                st.rerun()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Products", len(st.session_state.products))
        with col2:
            st.metric("Total Orders", len(st.session_state.orders))
        with col3:
            st.metric("Registered Drivers", len(st.session_state.drivers))
        with col4:
            total_revenue = sum([o['grand_total'] for o in st.session_state.orders])
            st.metric("Total Revenue", f"₹{total_revenue:,.2f}")
        
        st.markdown("---")
        
        tab1, tab2, tab3, tab4 = st.tabs(["📦 Manage Products", "📋 Orders", "🚛 Drivers", "📊 Analytics"])
        
        with tab1:
            st.markdown("### Product Management")
            
            subtab1, subtab2, subtab3 = st.tabs(["➕ Add Product", "✏️ Edit Product", "🗑️ Delete Product"])
            
            with subtab1:
                st.markdown("#### Add New Product")
                with st.form("add_product_admin"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        product_name = st.text_input("Product Name *")
                        category = st.selectbox(
                            "Category *",
                            ["Plants", "Furniture", "Fertilizers", "Building Materials", "Agricultural Supplies", "Hardware"]
                        )
                        price = st.number_input("Price per Unit (₹) *", min_value=0, value=1000)
                        unit = st.text_input("Unit (e.g., bags, saplings, sets) *", value="units")
                        min_quantity = st.number_input("Minimum Order Quantity *", min_value=1, value=10)
                        stock = st.number_input("Available Stock *", min_value=0, value=100)
                    
                    with col2:
                        supplier_name = st.text_input("Supplier/Business Name *")
                        location = st.selectbox("Location *", sorted(ASSAM_CITIES.keys()))
                        weight_kg = st.number_input("Weight per Unit (kg) *", min_value=0.1, value=10.0, step=0.1)
                        volume_m3 = st.number_input("Volume per Unit (m³) *", min_value=0.1, value=1.0, step=0.1)
                        description = st.text_area("Product Description *")
                    
                    submitted = st.form_submit_button("➕ Add Product", type="primary")
                    
                    if submitted:
                        if not product_name or not supplier_name or not description:
                            st.error("Please fill in all required fields marked with *")
                        else:
                            new_product = {
                                'id': max([p['id'] for p in st.session_state.products], default=0) + 1,
                                'name': product_name,
                                'category': category,
                                'price': price,
                                'weight_kg': weight_kg,
                                'volume_m3': volume_m3,
                                'min_quantity': min_quantity,
                                'unit': unit,
                                'supplier': supplier_name,
                                'location': location,
                                'coordinates': ASSAM_CITIES[location],
                                'description': description,
                                'stock': stock
                            }
                            st.session_state.products.append(new_product)
                            st.success(f"✅ Product '{product_name}' added successfully!")
                            st.balloons()
            
            with subtab2:
                st.markdown("#### Edit Existing Product")
                
                if len(st.session_state.products) == 0:
                    st.info("No products available to edit.")
                else:
                    product_options = {f"{p['name']} (ID: {p['id']})": p['id'] for p in st.session_state.products}
                    selected_product_name = st.selectbox("Select Product to Edit", list(product_options.keys()))
                    selected_product_id = product_options[selected_product_name]
                    
                    product_to_edit = next(p for p in st.session_state.products if p['id'] == selected_product_id)
                    
                    with st.form("edit_product_admin"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            edit_name = st.text_input("Product Name *", value=product_to_edit['name'])
                            edit_category = st.selectbox(
                                "Category *",
                                ["Plants", "Furniture", "Fertilizers", "Building Materials", "Agricultural Supplies", "Hardware"],
                                index=["Plants", "Furniture", "Fertilizers", "Building Materials", "Agricultural Supplies", "Hardware"].index(product_to_edit['category']) if product_to_edit['category'] in ["Plants", "Furniture", "Fertilizers", "Building Materials", "Agricultural Supplies", "Hardware"] else 0
                            )
                            edit_price = st.number_input("Price per Unit (₹) *", min_value=0, value=product_to_edit['price'])
                            edit_unit = st.text_input("Unit *", value=product_to_edit['unit'])
                            edit_min_quantity = st.number_input("Minimum Order Quantity *", min_value=1, value=product_to_edit['min_quantity'])
                            edit_stock = st.number_input("Available Stock *", min_value=0, value=product_to_edit['stock'])
                        
                        with col2:
                            edit_supplier = st.text_input("Supplier/Business Name *", value=product_to_edit['supplier'])
                            edit_location = st.selectbox("Location *", sorted(ASSAM_CITIES.keys()), index=sorted(ASSAM_CITIES.keys()).index(product_to_edit['location']) if product_to_edit['location'] in ASSAM_CITIES.keys() else 0)
                            edit_weight = st.number_input("Weight per Unit (kg) *", min_value=0.1, value=float(product_to_edit['weight_kg']), step=0.1)
                            edit_volume = st.number_input("Volume per Unit (m³) *", min_value=0.1, value=float(product_to_edit['volume_m3']), step=0.1)
                            edit_description = st.text_area("Product Description *", value=product_to_edit['description'])
                        
                        submitted = st.form_submit_button("💾 Save Changes", type="primary")
                        
                        if submitted:
                            product_to_edit['name'] = edit_name
                            product_to_edit['category'] = edit_category
                            product_to_edit['price'] = edit_price
                            product_to_edit['unit'] = edit_unit
                            product_to_edit['min_quantity'] = edit_min_quantity
                            product_to_edit['stock'] = edit_stock
                            product_to_edit['supplier'] = edit_supplier
                            product_to_edit['location'] = edit_location
                            product_to_edit['coordinates'] = ASSAM_CITIES[edit_location]
                            product_to_edit['weight_kg'] = edit_weight
                            product_to_edit['volume_m3'] = edit_volume
                            product_to_edit['description'] = edit_description
                            
                            st.success(f"✅ Product '{edit_name}' updated successfully!")
                            st.rerun()
            
            with subtab3:
                st.markdown("#### Delete Product")
                
                if len(st.session_state.products) == 0:
                    st.info("No products available to delete.")
                else:
                    product_options = {f"{p['name']} (ID: {p['id']})": p['id'] for p in st.session_state.products}
                    selected_product_name = st.selectbox("Select Product to Delete", list(product_options.keys()), key="delete_select")
                    selected_product_id = product_options[selected_product_name]
                    
                    product_to_delete = next(p for p in st.session_state.products if p['id'] == selected_product_id)
                    
                    st.warning(f"⚠️ You are about to delete: **{product_to_delete['name']}**")
                    st.write(f"Category: {product_to_delete['category']}")
                    st.write(f"Price: ₹{product_to_delete['price']:,}")
                    st.write(f"Stock: {product_to_delete['stock']} {product_to_delete['unit']}")
                    
                    col1, col2, col3 = st.columns([1, 1, 2])
                    with col1:
                        if st.button("🗑️ Confirm Delete", type="primary"):
                            st.session_state.products = [p for p in st.session_state.products if p['id'] != selected_product_id]
                            st.success(f"✅ Product deleted successfully!")
                            st.rerun()
                    with col2:
                        st.button("Cancel")
            
            st.markdown("---")
            st.markdown("### All Products")
            if len(st.session_state.products) > 0:
                df_products = pd.DataFrame(st.session_state.products)
                st.dataframe(df_products[['id', 'name', 'category', 'price', 'stock', 'supplier', 'location']], use_container_width=True)
            else:
                st.info("No products listed yet.")
        
        with tab2:
            st.markdown("### All Orders")
            if len(st.session_state.orders) > 0:
                df_orders = pd.DataFrame(st.session_state.orders)
                st.dataframe(df_orders[['id', 'product_name', 'buyer_name', 'quantity', 'grand_total', 'status', 'timestamp']], use_container_width=True)
            else:
                st.info("No orders placed yet.")
        
        with tab3:
            st.markdown("### Registered Drivers")
            if len(st.session_state.drivers) > 0:
                df_drivers = pd.DataFrame(st.session_state.drivers)
                st.dataframe(df_drivers[['id', 'name', 'phone', 'vehicle_type', 'location', 'available']], use_container_width=True)
            else:
                st.info("No drivers registered yet.")
        
        with tab4:
            st.markdown("### Analytics")
            
            if len(st.session_state.orders) > 0:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### Orders by Status")
                    status_counts = pd.DataFrame(st.session_state.orders)['status'].value_counts()
                    st.bar_chart(status_counts)
                
                with col2:
                    st.markdown("#### Revenue by Product")
                    revenue_by_product = {}
                    for order in st.session_state.orders:
                        product_name = order['product_name']
                        if product_name not in revenue_by_product:
                            revenue_by_product[product_name] = 0
                        revenue_by_product[product_name] += order['grand_total']
                    
                    st.bar_chart(revenue_by_product)
            else:
                st.info("No order data available for analytics.")

st.sidebar.markdown("---")
st.sidebar.markdown("**🌟 INDE Platform**")
st.sidebar.markdown("Making wholesale delivery convenient across Assam")
