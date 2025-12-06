#!/usr/bin/env python3
"""
Deity Comparison Visualization
Creates charts showing deity prominence across Vedas using percentage-based analysis
"""

import json
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

# Load the results
with open('/Users/ashris/Desktop/rigved/rigveda-web/yajurveda_analysis/deity_percentage_results.json', 'r') as f:
    results = json.load(f)

# Extract key deities for visualization
key_deities = [
    'Indra', 'Agni', 'Soma', 'Prajapati/Brahma', 'Rudra/Shiva',
    'Vishnu', 'Varuna', 'Maruts', 'Ashvins', 'Yama'
]

# Prepare data for charts
vedas = ['Rigveda', 'Yajurveda (Combined)', 'Atharvaveda']
colors = ['#8B4513', '#DAA520', '#2F4F4F']

# Create figure with subplots
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle('Deity Prominence Across Vedic Texts (Per 1000 Characters)', fontsize=16, fontweight='bold')

# 1. Bar chart comparing top deities across all three Vedas
ax1 = axes[0, 0]
x_pos = np.arange(len(key_deities))
bar_width = 0.25

for i, veda in enumerate(vedas):
    if veda in results:
        values = []
        for deity in key_deities:
            if deity in results[veda]:
                values.append(results[veda][deity]['per_1000_chars'])
            else:
                values.append(0)
        ax1.bar(x_pos + i * bar_width, values, bar_width, label=veda, color=colors[i], alpha=0.8)

ax1.set_xlabel('Deity', fontweight='bold')
ax1.set_ylabel('Mentions per 1000 characters', fontweight='bold')
ax1.set_title('Deity Prominence Comparison', fontweight='bold')
ax1.set_xticks(x_pos + bar_width)
ax1.set_xticklabels(key_deities, rotation=45, ha='right')
ax1.legend()
ax1.grid(axis='y', alpha=0.3)

# 2. Ratio chart showing YV/RV changes
ax2 = axes[0, 1]
ratios = []
deity_names = []

for deity in key_deities:
    if deity in results['Rigveda'] and deity in results['Yajurveda (Combined)']:
        rv_val = results['Rigveda'][deity]['per_1000_chars']
        yv_val = results['Yajurveda (Combined)'][deity]['per_1000_chars']
        if rv_val > 0:
            ratio = yv_val / rv_val
            ratios.append(ratio)
            deity_names.append(deity)

# Color bars based on increase/decrease
bar_colors = ['green' if r > 1.2 else 'red' if r < 0.8 else 'gray' for r in ratios]

bars = ax2.bar(range(len(ratios)), ratios, color=bar_colors, alpha=0.7)
ax2.axhline(y=1, color='black', linestyle='--', linewidth=1, label='No change')
ax2.set_xlabel('Deity', fontweight='bold')
ax2.set_ylabel('Yajurveda/Rigveda Ratio', fontweight='bold')
ax2.set_title('Deity Evolution: Yajurveda vs Rigveda', fontweight='bold')
ax2.set_xticks(range(len(deity_names)))
ax2.set_xticklabels(deity_names, rotation=45, ha='right')
ax2.grid(axis='y', alpha=0.3)

# Add value labels on bars
for bar, ratio in zip(bars, ratios):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
            f'{ratio:.2f}x', ha='center', va='bottom', fontsize=9)

# 3. Focus on Prajapati's dramatic rise
ax3 = axes[1, 0]
prajapati_data = []
for veda in vedas:
    if veda in results and 'Prajapati/Brahma' in results[veda]:
        prajapati_data.append(results[veda]['Prajapati/Brahma']['per_1000_chars'])
    else:
        prajapati_data.append(0)

bars = ax3.bar(vedas, prajapati_data, color=['#8B4513', '#FFD700', '#2F4F4F'], alpha=0.8)
ax3.set_ylabel('Mentions per 1000 characters', fontweight='bold')
ax3.set_title('The Prajapati Revolution: 23.93x Increase!', fontweight='bold', color='darkred')
ax3.grid(axis='y', alpha=0.3)

# Add value labels
for bar, val in zip(bars, prajapati_data):
    ax3.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.5,
            f'{val:.2f}', ha='center', va='bottom', fontweight='bold')

# Add explosion annotation
if len(prajapati_data) >= 2:
    ax3.annotate('23.93x\nINCREASE!',
                xy=(0.5, prajapati_data[0]),
                xytext=(0.5, 20),
                arrowprops=dict(arrowstyle='->', color='red', lw=2),
                fontsize=14, fontweight='bold', color='red',
                ha='center')

# 4. The myth of Rudra/Shiva increase
ax4 = axes[1, 1]
rudra_data = []
for veda in vedas:
    if veda in results and 'Rudra/Shiva' in results[veda]:
        rudra_data.append(results[veda]['Rudra/Shiva']['per_1000_chars'])
    else:
        rudra_data.append(0)

bars = ax4.bar(vedas, rudra_data, color=['#8B4513', '#8B0000', '#2F4F4F'], alpha=0.8)
ax4.set_ylabel('Mentions per 1000 characters', fontweight='bold')
ax4.set_title('The Rudra/Shiva Reality: DECREASES in Yajurveda!', fontweight='bold')
ax4.grid(axis='y', alpha=0.3)

# Add value labels
for bar, val in zip(bars, rudra_data):
    ax4.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.3,
            f'{val:.2f}', ha='center', va='bottom', fontweight='bold')

# Add decrease annotation
if len(rudra_data) >= 2:
    ax4.annotate('28% DECREASE\n(Myth Busted!)',
                xy=(1, rudra_data[1]),
                xytext=(1.5, 11),
                arrowprops=dict(arrowstyle='->', color='darkred', lw=2),
                fontsize=11, fontweight='bold', color='darkred',
                ha='center')

plt.tight_layout()
plt.savefig('/Users/ashris/Desktop/rigved/rigveda-web/yajurveda_analysis/deity_comparison_charts.png',
           dpi=150, bbox_inches='tight')
# plt.show()  # Commented out for non-interactive mode

print("\nVisualization saved as deity_comparison_charts.png")

# Create a second figure for detailed comparison
fig2, axes2 = plt.subplots(1, 2, figsize=(14, 6))
fig2.suptitle('Major Theological Shifts: Winners and Losers', fontsize=16, fontweight='bold')

# Winners chart
ax5 = axes2[0]
winners = [
    ('Prajapati/Brahma', 1.28, 30.66, 23.93),
    ('Adityas', 3.14, 6.03, 1.92),
    ('Vishnu', 5.82, 7.44, 1.28)
]

winner_names = [w[0] for w in winners]
rv_values = [w[1] for w in winners]
yv_values = [w[2] for w in winners]
ratios = [w[3] for w in winners]

x_pos = np.arange(len(winner_names))
bar_width = 0.35

bars1 = ax5.bar(x_pos - bar_width/2, rv_values, bar_width, label='Rigveda', color='#8B4513', alpha=0.8)
bars2 = ax5.bar(x_pos + bar_width/2, yv_values, bar_width, label='Yajurveda', color='#FFD700', alpha=0.8)

ax5.set_xlabel('Deity', fontweight='bold')
ax5.set_ylabel('Mentions per 1000 characters', fontweight='bold')
ax5.set_title('Biggest Winners (YV vs RV)', fontweight='bold', color='green')
ax5.set_xticks(x_pos)
ax5.set_xticklabels(winner_names)
ax5.legend()
ax5.grid(axis='y', alpha=0.3)

# Add ratio labels
for i, (bar1, bar2, ratio) in enumerate(zip(bars1, bars2, ratios)):
    y_pos = max(bar1.get_height(), bar2.get_height()) + 1
    ax5.text(i, y_pos, f'{ratio:.1f}x', ha='center', fontweight='bold', color='green')

# Losers chart
ax6 = axes2[1]
losers = [
    ('Ashvins', 21.04, 0.08, 0.004),
    ('Maruts', 35.64, 11.57, 0.32),
    ('Indra', 150.94, 71.11, 0.47),
    ('Soma', 96.90, 54.73, 0.56)
]

loser_names = [l[0] for l in losers]
rv_values = [l[1] for l in losers]
yv_values = [l[2] for l in losers]
ratios = [l[3] for l in losers]

x_pos = np.arange(len(loser_names))

bars1 = ax6.bar(x_pos - bar_width/2, rv_values, bar_width, label='Rigveda', color='#8B4513', alpha=0.8)
bars2 = ax6.bar(x_pos + bar_width/2, yv_values, bar_width, label='Yajurveda', color='#8B0000', alpha=0.8)

ax6.set_xlabel('Deity', fontweight='bold')
ax6.set_ylabel('Mentions per 1000 characters', fontweight='bold')
ax6.set_title('Biggest Losers (YV vs RV)', fontweight='bold', color='darkred')
ax6.set_xticks(x_pos)
ax6.set_xticklabels(loser_names)
ax6.legend()
ax6.grid(axis='y', alpha=0.3)

# Add ratio labels
for i, (bar1, bar2, ratio) in enumerate(zip(bars1, bars2, ratios)):
    y_pos = max(bar1.get_height(), bar2.get_height()) + 5
    ax6.text(i, y_pos, f'{ratio:.2f}x', ha='center', fontweight='bold', color='darkred')

plt.tight_layout()
plt.savefig('/Users/ashris/Desktop/rigved/rigveda-web/yajurveda_analysis/theological_shifts_charts.png',
           dpi=150, bbox_inches='tight')
# plt.show()  # Commented out for non-interactive mode

print("Theological shifts visualization saved as theological_shifts_charts.png")

# Print summary statistics
print("\n" + "="*60)
print("SUMMARY STATISTICS")
print("="*60)

print("\nText Lengths:")
print(f"Rigveda: 2,575,792 characters")
print(f"Yajurveda (Combined): 2,472,121 characters")
print(f"Atharvaveda: 1,467,573 characters")

print("\nMost Dramatic Changes (YV vs RV):")
print(f"1. Prajapati/Brahma: 23.93x INCREASE (1.28 → 30.66 per 1000)")
print(f"2. Ashvins: 0.004x (99.6% DECREASE) (21.04 → 0.08 per 1000)")
print(f"3. Maruts: 0.32x (68% decrease) (35.64 → 11.57 per 1000)")

print("\nRudra/Shiva Reality:")
print(f"Rigveda: 12.27 per 1000 chars")
print(f"Yajurveda: 8.78 per 1000 chars (28% DECREASE)")
print(f"Atharvaveda: 13.22 per 1000 chars")
print("CONCLUSION: Rudra prominence in Yajurveda is a MYTH!")

print("\nIndra's Collapse:")
print(f"Rigveda: 150.94 per 1000 chars (15% of all text!)")
print(f"Yajurveda: 71.11 per 1000 chars (53% decrease)")
print("From supreme warrior god to secondary deity")