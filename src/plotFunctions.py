import numpy as np
import matplotlib.pyplot as plt
def plot_differences(data_list, label, prog_dyn_data = None):
    mean_value = np.mean(data_list)
    mean_list = [mean_value] * len(data_list)
    plt.plot(mean_list, label=f'{label} Mean ({mean_value:.2f})', linestyle='--', color='black')
    if prog_dyn_data != None:
      plt.plot(prog_dyn_data, label=label + "(Prog dyn)", color='green')
    plt.plot(data_list, label=label + "(Blackbox)", color='red')

    plt.xlabel('Index')
    plt.ylabel('Error (Computed - Original)')
    plt.title(f'Differences of {label} between Computed and Original Values')
    plt.legend()
    plt.show()

def getColor(val):
  if val == 5:
    return 'red', 'orange'
  elif val == 4:
    return 'blue', 'cyan'
  elif val == 3:
    return 'green', 'green'
  
def plot_time(data_list, color, prog_dyn_data = None):
    mean_value = np.mean(data_list)
    mean_list = [mean_value] * len(data_list)
    plt.plot(mean_list, label=f'Moyenne temps pour BB ({mean_value:.2f})', linestyle='--', color='black')
    if prog_dyn_data != None:
      mean_value = np.mean(prog_dyn_data)
      mean_list = [mean_value] * len(prog_dyn_data)
      plt.plot(mean_list, label=f'Moyenne temps pour Prog dyn ({mean_value:.2f})', linestyle='--', color='gray')
    #plt.plot(data_list, label=label, color='red')
    
    prev = None
    start = 0
    values = []
    for i, num in enumerate(color):
      if prev != None:
        if num != prev:
          colbb, coldyn = getColor(prev)
          if num in values:
            plt.plot(np.arange(start, i, 1), data_list[start:i], color=colbb)
            if prog_dyn_data != None:
              plt.plot(np.arange(start, i, 1), prog_dyn_data[start:i], color=coldyn)
          else:
            plt.plot(np.arange(start, i, 1), data_list[start:i], label=f"Temps d'exécution (s) pour {prev} turbines (BB)", color=colbb)
            if prog_dyn_data != None:
              plt.plot(np.arange(start, i, 1), prog_dyn_data[start:i], label=f"Temps d'exécution (s) pour {prev} turbines (ProgDyn)", color=coldyn)
            values.append(num)
          start = i
      prev = num
    colBB, coldyn = getColor(prev)
    if num in values:
      plt.plot(np.arange(start, i + 1, 1), data_list[start:], color=colBB)
      if prog_dyn_data != None:
        plt.plot(np.arange(start, i + 1, 1), prog_dyn_data[start:], color=coldyn)
    else:
      plt.plot(np.arange(start, i + 1, 1), data_list[start:], label=f"Temps d'exécution pour {prev} turbines (BB)", color=getColor(prev))
      if prog_dyn_data != None:
        plt.plot(np.arange(start, i + 1, 1), prog_dyn_data[start:], label=f"Temps d'exécution (s) pour {prev} turbines (ProgDyn)", color=coldyn)

    plt.xlabel('Index')
    plt.ylabel('Temps d\'exécution (s)')
    plt.title(f"Temps d'exécution en secondes")
    plt.legend()
    plt.show()
