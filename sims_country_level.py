# %%
import json

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

total_mandates = 0
country_sims = np.zeros((n_sim, len(party_names)))


for okreg_name, o in data.items():
    parties_mandates_example = list(o["wykresRozkladu"].values())[0]
    num_mandates = sum(ms for _, ms in parties_mandates_example.items())

    total_mandates += num_mandates

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

    # normalize each row to add up to 100
    sums = sims.sum(axis=1) / 100
    sims = sims / sums[:, np.newaxis]
    assert np.allclose(sims.sum(axis=1), 100)

    country_sims += sims * num_mandates


# %%
country_results = country_sims / total_mandates
# %%
country_std = country_results.std(axis=0)
country_avg = country_results.mean(axis=0)

for party_name, avg, std in zip(party_names, country_avg, country_std):
    print(f"{party_name:8} {avg:.2f} ± {std:.2f}")
