import numpy as np
import matplotlib.pyplot as plt
def plot_differences(data_list, label):
    mean_value = np.mean(data_list)
    mean_list = [mean_value] * len(data_list)
    plt.plot(mean_list, label=f'{label} Mean ({mean_value:.2f})', linestyle='--', color='black')
    plt.plot(data_list, label=label, color='red')

    plt.xlabel('Index')
    plt.ylabel('Error (Computed - Original)')
    plt.title(f'Differences of {label} between Computed and Original Values')
    plt.legend()
    plt.show()

def getColor(val):
  if val == 5:
    return 'red'
  elif val == 4:
    return 'green'
  elif val == 3:
    return 'blue'
  
def plot_time(data_list, color):
    mean_value = np.mean(data_list)
    mean_list = [mean_value] * len(data_list)
    plt.plot(mean_list, label=f'Moyenne ({mean_value:.2f})', linestyle='--', color='black')
    #plt.plot(data_list, label=label, color='red')
    
    prev = None
    start = 0
    values = []
    for i, num in enumerate(color):
      if prev != None:
        if num != prev:
          col = getColor(prev)
          if num in values:
            plt.plot(np.arange(start, i, 1), data_list[start:i], color=col)
          else:
            plt.plot(np.arange(start, i, 1), data_list[start:i], label=f"Temps d'exécution (s) pour {prev} turbines", color=col)
            values.append(num)
          start = i
      prev = num
    if num in values:
      plt.plot(np.arange(start, i + 1, 1), data_list[start:], color=getColor(prev))
    else:
      plt.plot(np.arange(start, i + 1, 1), data_list[start:], label=f"Execution Time for {prev} turbines (s)", color=getColor(prev))

    plt.xlabel('Index')
    plt.ylabel('Error (Computed - Original)')
    plt.title(f"Temps d'exécution en secondes")
    plt.legend()
    plt.show()
