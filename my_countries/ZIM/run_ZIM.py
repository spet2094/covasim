# run baseline vs another scenario. Plot and save outputs
import covid_who as who
import covasim as cv
import sciris as sc
import matplotlib.pyplot as plt
from covid_who.locations.ZIM.sim import get_vaccine_sequence_strategy
import pandas as pd


def run_msim(func, n_runs, label, **kwargs):
    sims = sc.parallelize(func=func, iterkwargs={"seed": range(n_runs)}, **kwargs)
    msim = cv.MultiSim(sims, label=label, keep_people=True)
    msim.run(keep_people=True)
    msim.median()
    msim.sims[0].label = label # Temporary workaround until Covasim is updated
    return msim

if __name__ == "__main__":

    n_runs = 2
    location = "ZIM"

    iterkwargs = {"seed": range(n_runs)}

    # BASELINE: no change in vaccination
    msim = run_msim(func=who.get_vaccine_schedule_scenario_sim,
                    n_runs=n_runs,
                    label='baseline vaccination',
                    location='ZIM',
                    end_date='2021-06-30',
                    )
    # VULNERABLE: 75+, 65-74, 60-64, underlying illnesses, key workers, dense living, 50-59, 18-49, 5-17
    msim2 = run_msim(func=who.get_vaccine_schedule_scenario_sim,
                    n_runs=n_runs,
                    label= 'vulnerable',
                    location='ZIM',
                    end_date='2021-06-30',
                    people_per_day=10000,
                    vaccine_sequence_function = get_vaccine_sequence_strategy,
                    strat_string = 'vulnerable',
                    )
    # H CONTACTS: key workers, 18-49, dense living, underlying illness, 75+, 65-74, 60-64, 50-59, 5-17
    msim3 = run_msim(func=who.get_vaccine_schedule_scenario_sim,
                    n_runs=n_runs,
                    label='high contacts',
                    location='ZIM',
                    end_date='2021-06-30',
                    people_per_day=10000,
                    vaccine_sequence_function=get_vaccine_sequence_strategy,
                    strat_string='hcontacts',
                    )

    msims = [msim, msim2, msim3]
    merged = cv.MultiSim.merge(msims, base=True)
    merged.plot(to_plot = ['new_infections','cum_infections','new_diagnoses','cum_diagnoses','cum_deaths', 'new_vaccinated'], color_by_sim=True)


    # OUTPUT RESULTS TO EXCEL (copied from Tharindu's code)
    # msim.base_sim.to_excel(f"summary_baseline.xlsx")  # <--- exports the median projections for each scenario
    # msim2.base_sim.to_excel(f"summary_increased_vax.xlsx")  # <--- exports the median projections for each scenario
    # msim3.base_sim.to_excel(f"summary_age_vax.xlsx")  # <--- exports the median projections for each scenario

    # next step would be to go into excel and plot bar graphs of relevant variables for all scenarios


    # Example to check vaccine coverage
    df = pd.DataFrame(dict(age=msim.sims[0].people.age,
                           baseline=msim.sims[0].people.vaccinated,
                           scen1 = msim2.sims[0].people.vaccinated,
                           scen2=msim3.sims[0].people.vaccinated))


    # plt.figure()
    plt.figure()
    df.groupby('age')['baseline'].count().plot.bar()
    df.groupby('age')['baseline'].sum().plot.bar(color='r')
    plt.title('No additional vaccines')

    # plt.figure()
    # df.groupby('age')['increased'].count().plot.bar()
    # df.groupby('age')['increased'].sum().plot.bar(color='r')
    # plt.title('Increased vaccines by cohort')
    plt.figure()
    df.groupby('age')['scen1'].count().plot.bar()
    df.groupby('age')['scen1'].sum().plot.bar(color='r')
    plt.title('vulnerable')

    # plt.figure()
    # df.groupby('age')['cohort'].count().plot.bar()
    # df.groupby('age')['cohort'].sum().plot.bar(color='r')
    # plt.title('Increased vaccines by age')

    plt.figure()
    df.groupby('age')['scen2'].count().plot.bar()
    df.groupby('age')['scen2'].sum().plot.bar(color='r')
    plt.title('high contacts')
