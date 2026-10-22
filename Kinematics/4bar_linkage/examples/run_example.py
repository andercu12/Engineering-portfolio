"""Reproduce a crank-rocker example using the original solver functions."""
import argparse
import csv
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from src.model import build_four_bar_model, build_numeric_functions
from src.solvers import solve_position, solve_velocity, solve_acceleration
from src.visualization import joint_coordinates

LENGTHS = (150, 50, 120, 100)
THETA_START = np.radians(45)
OMEGA_INPUT = 2.0


def sample_cycle(count=361):
    functions = build_numeric_functions(build_four_bar_model())
    guess = np.radians([45, 90])
    rows, points = [], []
    for t in np.linspace(0, 2*np.pi/OMEGA_INPUT, count):
        theta2 = THETA_START + OMEGA_INPUT*t
        theta3, theta4 = solve_position(LENGTHS, theta2, functions['F'], guess)
        guess = [theta3, theta4]
        angles = (theta2, theta3, theta4)
        omega3, omega4 = solve_velocity(LENGTHS, angles, OMEGA_INPUT, functions['J'])
        alpha3, alpha4 = solve_acceleration(LENGTHS, angles, (OMEGA_INPUT, omega3, omega4),
                                          0.0, functions['J'], functions['J_dot'])
        residual = float(np.max(np.abs(functions['F'](*LENGTHS, *angles))))
        O2, A, B, O4 = joint_coordinates(LENGTHS, angles)
        rows.append([t, *angles, OMEGA_INPUT, omega3, omega4, 0.0, alpha3, alpha4,
                     A[0], A[1], B[0], B[1], residual])
        points.append([O2, A, B, O4])
    return np.asarray(rows), np.asarray(points)


def save_figures(rows, points, output):
    colors = ['#447eaa', '#d29542', '#4d8a6b']
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), layout='constrained')
    ax = axes[0]
    ax.plot(points[:,2,0], points[:,2,1], '--', color='#888888', lw=1, label='Joint B path')
    for i, (color, label) in enumerate(zip(colors, ['Input crank L2','Coupler L3','Output rocker L4'])):
        ax.plot(points[0,i:i+2,0], points[0,i:i+2,1], '-o', color=color, lw=3, label=label)
    ax.plot([0,LENGTHS[0]], [0,0], '--', color='#444444', lw=2, label='Ground L1')
    ax.scatter([0,LENGTHS[0]], [0,0], marker='^', color='#333333', s=100, zorder=5)
    for label, xy in zip(['O2','A','B','O4'], points[0]):
        ax.annotate(label, xy, xytext=(7,8), textcoords='offset points')
    ax.set(xlabel='X [mm]', ylabel='Y [mm]', title='Initial configuration · input angle 45°',
           xlim=(-65,240), ylim=(-90,180))
    ax.set_aspect('equal')
    ax.grid(alpha=0.2)
    ax.legend(frameon=False, fontsize=8, loc='upper left')
    for col, label, color in [(2,'Coupler θ3',colors[1]),(3,'Rocker θ4',colors[2])]:
        axes[1].plot(np.degrees(rows[:,1]), np.degrees(rows[:,col]), label=label, color=color)
    axes[1].set(xlabel='Input angle θ2 [deg]', ylabel='Absolute angle [deg]', title='One input revolution')
    axes[1].grid(alpha=0.2)
    axes[1].legend(frameon=False)
    fig.suptitle('Four-bar linkage · crank-rocker example', fontsize=15)
    fig.savefig(output/'mechanism_example.png', dpi=180)
    plt.close(fig)
    fig, axes = plt.subplots(2,1,figsize=(8,6),sharex=True,layout='constrained')
    for axis, cols, ylabel in [(axes[0],(5,6),'Angular velocity [rad/s]'),
                               (axes[1],(8,9),'Angular acceleration [rad/s²]')]:
        for col,label,color in zip(cols,['Coupler','Rocker'],colors[1:]):
            axis.plot(rows[:,0],rows[:,col],label=label,color=color)
        axis.set_ylabel(ylabel)
        axis.grid(alpha=0.2)
        axis.legend(frameon=False)
    axes[1].set_xlabel('Time [s]')
    fig.suptitle('Constant input speed: 2 rad/s · input acceleration: 0 rad/s²')
    fig.savefig(output/'kinematics.png',dpi=180)
    plt.close(fig)


def save_gif(output):
    rows, points = sample_cycle(81)
    fig, ax = plt.subplots(figsize=(6,5),layout='constrained')
    ax.set(xlim=(-65,240),ylim=(-90,180),xlabel='X [mm]',ylabel='Y [mm]')
    ax.set_aspect('equal')
    ax.grid(alpha=0.2)
    ax.plot([0,LENGTHS[0]],[0,0],'--',color='#555555')
    ax.plot(points[:,2,0],points[:,2,1],'--',color='#aaaaaa',lw=1)
    lines=[ax.plot([],[],'-o',lw=3,color=color)[0] for color in ['#447eaa','#d29542','#4d8a6b']]
    def update(i):
        for j,line in enumerate(lines):
            line.set_data(points[i,j:j+2,0],points[i,j:j+2,1])
        ax.set_title(f'Crank-rocker · t = {rows[i,0]:.2f} s\nω2 = 2 rad/s · α2 = 0 rad/s²')
        return lines
    animation=FuncAnimation(fig,update,frames=80)
    animation.save(output/'mechanism_motion.gif',writer=PillowWriter(fps=80/np.pi),dpi=100)
    plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--gif',action='store_true',help='Also export a short GIF')
    parser.add_argument('--output',type=Path,default=Path('results'))
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    rows,points=sample_cycle()
    header=['time_s','theta2_rad','theta3_rad','theta4_rad','omega2_rad_s','omega3_rad_s',
            'omega4_rad_s','alpha2_rad_s2','alpha3_rad_s2','alpha4_rad_s2',
            'A_x_mm','A_y_mm','B_x_mm','B_y_mm','closure_residual_mm']
    with (args.output/'crank_rocker.csv').open('w',newline='') as file:
        writer=csv.writer(file);writer.writerow(header);writer.writerows(rows)
    save_figures(rows,points,args.output)
    if args.gif:save_gif(args.output)
    initial=rows[0]
    report=('Crank-rocker example\nLengths [mm]: 150, 50, 120, 100\n'
            f'Initial angles [deg]: {np.degrees(initial[1:4])}\n'
            f'Initial angular velocities [rad/s]: {initial[4:7]}\n'
            f'Initial angular accelerations [rad/s²]: {initial[7:10]}\n'
            f'Cycle duration [s]: {rows[-1,0]:.9f}\n'
            f'Maximum loop residual [mm]: {rows[:,-1].max():.3e}\n')
    (args.output/'example_output.txt').write_text(report,encoding='utf-8')
    print(report)


if __name__=='__main__':main()
