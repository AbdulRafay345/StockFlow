from hero import HeroScreen
from dashboard import InventoryApp

if __name__ == "__main__":
    # Create the dashboard first but keep it hidden
    app = InventoryApp()
    app.withdraw()

    # Show the hero screen on top
    def launch_dashboard():
        app.state("zoomed")
        app.deiconify()

    hero = HeroScreen(app, on_launch=launch_dashboard)

    # Start the event loop (drives both windows)
    app.mainloop()