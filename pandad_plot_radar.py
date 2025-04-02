import matplotlib
matplotlib.use('Qt5agg')  # Switch to Qt5 backend
import cereal.messaging as messaging
import cantools.database
from opendbc.car.can_definitions import CanData
import matplotlib.animation
import matplotlib.collections
import numpy as np
import matplotlib.pyplot as plt

db = cantools.database.load_file(
    "./opendbc/dbc/u_radar.dbc"
)  # Load the DBC file for the radar configuration

rolling_counter = 0
x, y, obj_id = [], [], []

fig, ax = plt.subplots(figsize=(10, 8))
sc = ax.scatter([], [], c='blue', label='Radar Points', alpha=0.7)
ax.set_xlim(-40, 40)  # Set x-axis limits
ax.set_ylim(0, 220)  # Set y-axis limits

ax.set_title("Radar Points Visualization")
ax.set_xlabel("Longitudinal Distance (m)")
ax.set_ylabel("Lateral Distance (m)")
ax.grid(True)
ax.legend()

logcan = messaging.sub_sock('can', timeout=2000)  # Subscribe to CAN messages

def animate_radar(frame):
    print("Animating frame:", frame)
    for can in messaging.drain_sock(logcan, wait_for_one=True):
        for msg in can.can:
            if msg.address == 0x60A:
                sc.set_offsets(np.empty((0, 2)))  # Clear previous points
                x.clear()
                y.clear()
                obj_id.clear()
            if msg.address == 0x60B:
                dat = db.decode_message(msg.address, msg.dat)
                x.append(dat.get('DistLong', 0))
                y.append(dat.get('DistLat', 0))
                obj_id.append(dat.get('ID', 0))
                sc.set_offsets(np.c_[x, y])  # Update scatter plot with new points
    for i, txt in enumerate(obj_id):
        # Annotate each point with its object ID
        ax.annotate(f'ID: {txt}', (x[i], y[i]), textcoords="offset points", xytext=(0,5), ha='center', fontsize=8, color='red')
    return sc, 

def init():
    """Initialization function for the animation."""
    sc.set_offsets(np.empty((0, 2)))  # Clear previous points
    return sc,

def main():
    print("Starting animation...")
    
    anim = matplotlib.animation.FuncAnimation(fig, animate_radar,
                                              init_func=init,
                                              interval=100, blit=True, save_count=0)
    plt.show()  # Show the plot window and start the animation
        

if __name__ == "__main__":
    main()