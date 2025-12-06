#!/usr/bin/env python3
"""
Visualization of Vishnu, Rudra, and Prajapati trajectories across Vedas
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

# Data from our analysis
deities_data = {
    'Vishnu': {
        'Rigveda': 106,
        'Yajurveda': 112,
        'Atharvaveda': 57
    },
    'Rudra': {
        'Rigveda': 207,
        'Yajurveda': 100,
        'Atharvaveda': 140
    },
    'Prajapati': {
        'Rigveda': 14,
        'Yajurveda': 185,
        'Atharvaveda': 82
    }
}

# Context shift data
context_shifts = {
    'Vishnu': {
        'Ritual': {'RV': 33, 'YV': 72},
        'Creation': {'RV': 8, 'YV': 40},
        'Power': {'RV': 28, 'YV': 50}
    },
    'Rudra': {
        'Praise': {'RV': 65, 'YV': 20},
        'Ritual': {'RV': 38, 'YV': 64},
        'Power': {'RV': 60, 'YV': 51}
    },
    'Prajapati': {
        'Ritual': {'RV': 6, 'YV': 158},
        'Creation': {'RV': 4, 'YV': 144},
        'Power': {'RV': 3, 'YV': 125}
    }
}

# Create figure with subplots
fig = plt.figure(figsize=(16, 10))
fig.suptitle('Deity Trajectories: Vishnu, Rudra, and Prajapati', fontsize=16, fontweight='bold')

# 1. Overall trajectory plot
ax1 = plt.subplot(2, 3, (1, 2))
vedas = ['Rigveda', 'Yajurveda', 'Atharvaveda']
x = np.arange(len(vedas))

for deity, data in deities_data.items():
    values = [data[veda] for veda in vedas]
    if deity == 'Vishnu':
        ax1.plot(x, values, 'o-', label=deity, linewidth=2, markersize=8, color='blue')
    elif deity == 'Rudra':
        ax1.plot(x, values, 's-', label=deity, linewidth=2, markersize=8, color='red')
    else:  # Prajapati
        ax1.plot(x, values, '^-', label=deity, linewidth=2, markersize=8, color='green')

ax1.set_xticks(x)
ax1.set_xticklabels(vedas)
ax1.set_ylabel('Number of Mentions', fontweight='bold')
ax1.set_title('Deity Trajectories Across Vedas', fontweight='bold')
ax1.legend(loc='upper left')
ax1.grid(True, alpha=0.3)

# Add annotations for dramatic changes
ax1.annotate('Prajapati\nExplosion\n+1221%',
            xy=(1, 185), xytext=(1.3, 220),
            arrowprops=dict(arrowstyle='->', color='green', lw=2),
            fontsize=10, color='green', fontweight='bold')

ax1.annotate('Rudra\nDecline\n-52%',
            xy=(1, 100), xytext=(0.6, 50),
            arrowprops=dict(arrowstyle='->', color='red', lw=1.5),
            fontsize=10, color='red')

# 2. Percentage change bar chart
ax2 = plt.subplot(2, 3, 3)
changes = {
    'Vishnu': ((112/106 - 1) * 100),
    'Rudra': ((100/207 - 1) * 100),
    'Prajapati': ((185/14 - 1) * 100)
}

# Cap Prajapati for visualization
display_changes = {
    'Vishnu': changes['Vishnu'],
    'Rudra': changes['Rudra'],
    'Prajapati': min(changes['Prajapati'], 500)  # Cap at 500% for display
}

bars = ax2.bar(display_changes.keys(), display_changes.values(),
               color=['blue', 'red', 'green'], alpha=0.7)

# Color bars based on positive/negative
for bar, value in zip(bars, display_changes.values()):
    if value < 0:
        bar.set_color('darkred')
    elif value > 100:
        bar.set_color('darkgreen')

ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
ax2.set_ylabel('% Change (RV to YV)', fontweight='bold')
ax2.set_title('Deity Evolution: Rigveda to Yajurveda', fontweight='bold')

# Add actual value labels
for bar, (deity, value) in zip(bars, changes.items()):
    if deity == 'Prajapati':
        ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 10,
                f'{value:.0f}%', ha='center', va='bottom', fontweight='bold')
    else:
        ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 5,
                f'{value:.1f}%', ha='center', va='bottom')

# 3-5. Context shift charts for each deity
for idx, (deity, contexts) in enumerate(context_shifts.items(), 4):
    ax = plt.subplot(2, 3, idx)

    context_names = list(contexts.keys())
    rv_values = [contexts[c]['RV'] for c in context_names]
    yv_values = [contexts[c]['YV'] for c in context_names]

    x_pos = np.arange(len(context_names))
    width = 0.35

    bars1 = ax.bar(x_pos - width/2, rv_values, width, label='Rigveda', alpha=0.8)
    bars2 = ax.bar(x_pos + width/2, yv_values, width, label='Yajurveda', alpha=0.8)

    # Color coding
    if deity == 'Vishnu':
        color = 'blue'
    elif deity == 'Rudra':
        color = 'red'
    else:
        color = 'green'

    for bar in bars1:
        bar.set_color(color)
        bar.set_alpha(0.5)
    for bar in bars2:
        bar.set_color(color)
        bar.set_alpha(0.9)

    ax.set_xlabel('Context Type', fontsize=10)
    ax.set_ylabel('Mentions', fontsize=10)
    ax.set_title(f'{deity} Context Shift', fontweight='bold', color=color)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(context_names, rotation=45, ha='right')
    ax.legend(fontsize=8)
    ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('/Users/ashris/Desktop/rigved/rigveda-web/yajurveda_analysis/deity_trajectories.png',
           dpi=150, bbox_inches='tight')

print("Deity trajectory visualization saved as deity_trajectories.png")

# Create a second figure for theological interpretation
fig2, axes = plt.subplots(1, 3, figsize=(15, 5))
fig2.suptitle('The Three Theological Trajectories', fontsize=14, fontweight='bold')

# Vishnu - The Adapter
ax = axes[0]
stages = ['Helper\nDeity', 'Ritual\nPresence', 'Cosmic\nPervader']
values = [30, 60, 90]  # Conceptual progression
ax.plot(stages, values, 'o-', color='blue', linewidth=3, markersize=10)
ax.fill_between(range(len(stages)), 0, values, alpha=0.3, color='blue')
ax.set_ylabel('Theological Importance', fontweight='bold')
ax.set_title('Vishnu: The Adapter', color='blue', fontweight='bold')
ax.set_ylim(0, 100)
ax.grid(axis='y', alpha=0.3)

# Rudra - The Resistor
ax = axes[1]
stages = ['Storm\nGod', 'Managed\nDanger', 'Marginal\nHealer']
values = [70, 40, 30]  # Declining trajectory
ax.plot(stages, values, 's-', color='red', linewidth=3, markersize=10)
ax.fill_between(range(len(stages)), 0, values, alpha=0.3, color='red')
ax.set_ylabel('Theological Importance', fontweight='bold')
ax.set_title('Rudra: The Resistor', color='red', fontweight='bold')
ax.set_ylim(0, 100)
ax.grid(axis='y', alpha=0.3)

# Prajapati - The Revolutionary
ax = axes[2]
stages = ['Minor\nCreator', 'Sacrifice\nLord', 'Supreme\nCreator']
values = [10, 60, 95]  # Explosive growth
ax.plot(stages, values, '^-', color='green', linewidth=3, markersize=10)
ax.fill_between(range(len(stages)), 0, values, alpha=0.3, color='green')
ax.set_ylabel('Theological Importance', fontweight='bold')
ax.set_title('Prajapati: The Revolutionary', color='green', fontweight='bold')
ax.set_ylim(0, 100)
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('/Users/ashris/Desktop/rigved/rigveda-web/yajurveda_analysis/theological_trajectories.png',
           dpi=150, bbox_inches='tight')

print("Theological trajectories saved as theological_trajectories.png")

# Summary statistics
print("\n" + "="*60)
print("DEITY TRAJECTORY SUMMARY")
print("="*60)

for deity, data in deities_data.items():
    print(f"\n{deity}:")
    print(f"  Rigveda: {data['Rigveda']} mentions")
    print(f"  Yajurveda: {data['Yajurveda']} mentions")
    print(f"  Change: {((data['Yajurveda']/data['Rigveda'] - 1) * 100):.1f}%")

    if deity in context_shifts:
        print(f"  Key context shifts:")
        for context, values in context_shifts[deity].items():
            change = ((values['YV']/max(values['RV'], 1) - 1) * 100)
            print(f"    {context}: {change:+.0f}%")

print("\n" + "="*60)
print("KEY FINDING: Prajapati's 1221% increase represents the most")
print("dramatic theological shift in Vedic literature, marking the")
print("transition from warrior gods to creator theology.")
print("="*60)