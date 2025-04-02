import matplotlib
matplotlib.use('Qt5Agg')  # Switch to Qt5 backend
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Sample data generation (replace this with your actual radar data)
# Let's assume we have 50 frames of data with varying points
np.random.seed(42)
num_frames = 50
data = [np.random.rand(np.random.randint(20, 50), 2) * 100 for _ in range(num_frames)]

# Create figure and axis
fig, ax = plt.subplots(figsize=(10, 8))
scatter = ax.scatter([], [], s=50, c='blue', alpha=0.6)

# Set plot limits
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)

# Add labels and title
ax.set_xlabel('X Coordinate')
ax.set_ylabel('Y Coordinate')
ax.set_title('Radar Point Data Animation')
ax.grid(True)

# Initialization function
def init():
    scatter.set_offsets(np.empty((0, 2)))
    return scatter,

# Animation update function
def update(frame):
    # Update scatter plot with new frame data
    scatter.set_offsets(data[frame])
    return scatter,

# Create animation
anim = FuncAnimation(fig, update, init_func=init,
                    frames=num_frames,
                    interval=200,  # milliseconds between frames
                    blit=True)

# Display the animation
plt.show()

# Optional: Save the animation as a video file
# anim.save('radar_animation.mp4', writer='ffmpeg', fps=5)