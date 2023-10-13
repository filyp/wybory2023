# %%
import json

import matplotlib.pyplot as plt
import numpy as np

# %%
# load okregi.json
with open("okregi.json") as f:
    data = json.load(f)

party_names = ["PIS", "KONF", "KO", "TD", "LEWICA"]

np.random.seed(0)
n_sim = 10000
epsilon = 0.1

party_colors_dict = dict(
    PIS=[0.14901960784313725, 0.21568627450980393, 0.47058823529411764],
    LEWICA=[0.6705882352941176, 0.0784313725490196, 0.3568627450980392],
    KONF=[0.0, 0.0, 0.0],
    TD=[0.8627450980392157, 0.7647058823529411, 0.06274509803921569],
    KO=[0.0, 0.26666666666666666, 0.5843137254901961],
    BIAŁY=[1.0, 1.0, 1.0],
)
party_colors = [party_colors_dict[party_name] for party_name in party_names]

# %%


def get_avg_mandate_assignments(unnormalized_sims, num_mandates):
    # normalize each row to add up to 100
    sums = unnormalized_sims.sum(axis=1) / 100
    sims = unnormalized_sims / sums[:, np.newaxis]

    all_simulated_mandate_assignments = []
    for sim in sims:
        # Dhondt method
        mandate_assignments = np.zeros_like(sim, dtype=int)
        divisors = np.ones_like(sim, dtype=int)
        for i in range(num_mandates):
            # find max ind in sim/divisors
            # print(i)
            # print(f"divisors:            {divisors}")
            # print(sim / divisors)
            max_ind = np.argmax(sim / divisors)
            # print(f"max_ind: {max_ind}")

            # assign mandate to max_ind
            mandate_assignments[max_ind] += 1
            divisors[max_ind] += 1
            # print(f"mandate_assignments: {mandate_assignments}")
            # print()
        all_simulated_mandate_assignments.append(mandate_assignments)

    all_simulated_mandate_assignments = np.array(all_simulated_mandate_assignments)
    return all_simulated_mandate_assignments.mean(axis=0)


# %%
max_val = 0.044
plt.ioff()
# max_val_total = 0

markdown = """
# Wzmocnij swój głos

Jak głos oddany na pewną partę wpływa na przydział mandatów w okręgu.

Dla każdego okręgu przeprowadzane jest 10000 symulacji, losując wyniki
wg podanych średnich i odchyleń standardowych.

Następnie dla każdej sytuacji porównujemy wariant gdzie głosujemy na
partię X z wariantem gdzie nie głosujemy na nic.

Na wykresach pokazana jest wartość oczekiwana tego jak głos wpłynie
na przydział mandatów w okręgu, wyliczona jako średnia z 10000 symulacji.

Dane wzięte z:
[pogonimypis.pl](https://pogonimypis.pl/) (A dokładnie [stąd](https://github.com/krozkwitalski/wybory/blob/master/symulacja.ts).)
"""

for okreg_name, o in data.items():
    parties_mandates_example = list(o["wykresRozkladu"].values())[0]
    num_mandates = sum(ms for _, ms in parties_mandates_example.items())

    markdown += f"## {okreg_name}\n"

    markdown += f"```\n"
    for party_name in party_names:
        markdown += f"{party_name:6}  {o['procentyWOkreguSrednia'][party_name]:4.1f} ± {o['odchylenieWOkregu'][party_name]:3.1f}\n"
    markdown += f"```\n"

    # create sims
    sims = []
    for party_name in party_names:
        sims.append(
            np.random.normal(
                loc=o["procentyWOkreguSrednia"][party_name],
                scale=o["odchylenieWOkregu"][party_name],
                size=n_sim,
            )
        )
    sims = np.array(sims).T

    base_assignment = get_avg_mandate_assignments(sims, num_mandates)

    changes = dict()
    for party_name in ["KO", "TD", "LEWICA"]:
        # now add some small change to the sims
        index = party_names.index(party_name)

        modded_sims = sims.copy()
        modded_sims[:, index] += epsilon

        modded_assignment = get_avg_mandate_assignments(modded_sims, num_mandates)

        changes[party_name] = modded_assignment - base_assignment

    # plot to the file
    # use 3 subplots
    fig, axs = plt.subplots(1, 3, figsize=(15, 5))
    # global title is okreg name
    fig.suptitle(okreg_name)

    # # use common scale for all plots, symmetrical
    # local_max_val = max(abs(change).max() for change in changes.values())
    # max_val_total = max(max_val_total, local_max_val)

    for i, (party_name, change) in enumerate(changes.items()):
        axs[i].bar(party_names, change, color=party_colors)
        axs[i].set_title(f"Głos na {party_name}")
        axs[i].set_ylim(-max_val, max_val)
        # also print a black line at 0
        axs[i].axhline(0, color="black")

    plot_filename = f"plots/{okreg_name.replace(' ', '_')}.png"
    plt.savefig(plot_filename)

    markdown += f"![]({plot_filename})\n\n"


# %%
# save markdown
filename = "README.md"

with open(filename, "w") as f:
    f.write(markdown)


# print(max_val_total)


markdown += """
# Appendix

Jeden głos rzadko kiedy zmienia przydział mandatów. Dlatego żeby zmniejszyć konieczną
liczbę symulacji, zamiast jednego głosu oddanego na partię X, dodaje jej
̣0.1 punkta procentowego do poparcia w okręgu.

Nie wygląda żeby było to za dużo, bo gdy zmieniłem tą liczbę na 0.01, to wyniki
nie zmieniły się znacząco.
"""