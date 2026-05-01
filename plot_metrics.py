import matplotlib.pyplot as plt
import numpy as np

# Data: Metrics and Scores
metrics = ['BLEU-4', 'ROUGE-1', 'ROUGE-2', 'ROUGE-L']
base_scores = [24.67, 30.46, 8.58, 14.99]
tuned_scores = [51.43, 42.76, 19.06, 27.77]

# Set up the grouped bar chart parameters
x = np.arange(len(metrics))
width = 0.35  # width of the bars

# Style Settings
plt.style.use('ggplot')
fig, ax = plt.subplots(figsize=(10, 6))

# Plot the bars
rects1 = ax.bar(x - width/2, base_scores, width, label='Qwen-1.5B (Untuned Baseline)', color='#E15759')
rects2 = ax.bar(x + width/2, tuned_scores, width, label='UCKG-Qwen-1.5B (Fine-Tuned)', color='#4E79A7')

# Labels and Title
ax.set_ylabel('Score (%)', fontsize=12, fontweight='bold')
ax.set_title('Supervised Fine-Tuning (SFT) Impact on Reasoning', fontsize=16, fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(metrics, fontsize=12)
ax.set_ylim(0, 70)
ax.legend(fontsize=12, loc='upper left')

# Function to automatically attach text labels above the bars
def autolabel(rects):
    """Attach a text label above each bar, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        ax.annotate(f'{height:.1f}%',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=11, fontweight='bold')

autolabel(rects1)
autolabel(rects2)

# Final Polish
plt.tight_layout()
output_file = 'evaluation_chart_sft_comparison.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"Chart saved to {output_file}")
