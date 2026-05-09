# ❖ StockFlow
### *Modern Inventory Ecosystem & Warehouse Optimization*

**StockFlow** is a high-performance, visually stunning inventory management system designed for modern warehouses. Built with Python and powered by advanced data structures, it combines a premium user experience with intelligent logistics algorithms.

---

## 🚀 Key Features

### 📊 Intelligent Dashboard
Get a bird's-eye view of your business with real-time KPIs, including total inventory value, category breakdowns, and critical low-stock alerts.

### 🌳 High-Performance Catalogue (AVL Tree)
The system uses a **Self-Balancing AVL Tree** to manage thousands of items with $O(\log n)$ efficiency. This ensures lightning-fast search, insertion, and deletion, no matter how large your inventory grows.

### 🗺️ Warehouse Pathfinding (A* Algorithm)
StockFlow doesn't just track items—it helps you pick them. Using an **A* Pathfinding algorithm**, the system calculates the most efficient route through a 20x20 warehouse grid to collect multiple items, significantly reducing picker travel time.

### 🔄 Seamless Transactions
Track every purchase and sale with automated stock updates and detailed transaction logging. The system maintains a full history of stock movements for audit and analysis.

### 🎨 Premium Aesthetics
Experience a "Donezo-inspired" sage green theme with custom-built UI components:
*   **Card-based Layouts** with soft shadows.
*   **Animated Navigation** and hover effects.
*   **Modern Data Tables** with optimized scrolling.
*   **Crisp Typography** using High-DPI aware rendering.

---

## 🛠️ Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Language** | Python 3.x |
| **UI Framework** | Tkinter (Custom Styled) |
| **Data Structures** | AVL Tree (Self-balancing BST) |
| **Algorithms** | A* Search, Nearest-Neighbor Heuristic (TSP) |
| **Storage** | Flat-file (TSV) for reliability and transparency |

---

## 📁 Project Structure

*   `main.py` - The entry point; handles the Hero Screen and Dashboard lifecycle.
*   `dashboard.py` - The heart of the UI; contains the main application logic and custom components.
*   `hero.py` - A beautiful splash screen to welcome users.
*   `functions.py` - Core backend logic, including the AVL Tree implementation and file I/O.
*   `pathfinding.py` - Warehouse grid logic and A* route optimization.
*   `catalogue.txt` - Persistent storage for all inventory items.
*   `transactions.txt` - Historical log of all stock movements.

---

## 📥 Installation & Usage

1.  **Prerequisites**: Ensure you have Python 3.8+ installed.
2.  **Clone/Download**: Download the project files to your local machine.
3.  **Run**: Navigate to the project directory and execute:
    ```bash
    python main.py
    ```

---

## 📝 Data Format

The `catalogue.txt` file uses a Tab-Separated Value (TSV) format:
`Name	Description	Category	Price	Quantity	Loc_X	Loc_Y`

The `transactions.txt` file logs events in the following format:
`[Timestamp] TYPE | Item Name | Qty: X`

---

*Built with ❤️ for efficient logistics.*
