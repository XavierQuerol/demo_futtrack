import pandas as pd
import os
from datetime import datetime, timedelta
import numpy as np
import plotly.express as px

def send_fig():

    files = os.listdir("./fitxers")

    players = ["corts", "coco", 
            "piu", "pit", "zet", "carri", "kuman",
            "kiki", "aleix","arnau", "guillem", "kule"]

    player_times = {player: 0 for player in players}

    PARTITS = pd.DataFrame(columns = ["dia", "rival", "local", "tipus"])
    GOLS = pd.DataFrame(columns = ["golejador", "assistent", "gol CF", "minut", "part", "dia partit"] + players)
    MINUTS_JUGATS = pd.DataFrame(columns = ["jugador", "minuts jugats", "part", "dia partit"])
    CANVIS = pd.DataFrame(columns = ["minut", "part", "dia partit"] + players)



    for file in files:
        with open(f"fitxers/{file}", "r") as f:
            parts = f.read()
            parts = parts.split("\n\n")
            info_partit = parts[0].split("\n")

            tipus_partit = info_partit[0]
            rival = info_partit[1]
            dia_partit = datetime.strptime(info_partit[2], "%d/%m/%Y")
            local = info_partit[3]

            info_partit = {"tipus": tipus_partit, "rival": rival, 
                        "dia":dia_partit, "local": local}
            
            PARTITS = pd.concat((PARTITS, pd.DataFrame([info_partit])))

            
            for p, part in enumerate(parts[1:]):

                player_times2 = {player: timedelta() for player in players}
                
                accions = part.split("\n")
                equip = accions[0].split(":")[1].split(" ")

                new_row = {"minut": timedelta(minutes=20),
                "part": p, 
                "dia partit": dia_partit}
                players_in_equip = {player: True if player in equip else False for player in players}
                new_row.update(players_in_equip)
                CANVIS = pd.concat((CANVIS, pd.DataFrame([new_row])))


                for jugador in equip:
                    player_times[jugador] = timedelta(minutes=20)

                for i in range(1,len(accions)):
                    accio = accions[i]
                    if "temps-mort" in accio:
                        pass

                    elif "gol" in accio:
                        accio = accio.split(" ")
                        temps = accio[0].split(".")
                        temps = timedelta(minutes=int(temps[0]), seconds=int(temps[1]))
                        new_row = {"minut": temps, 
                                "part": p, 
                                "dia partit": dia_partit}
                        if "rival" not in accio:
                            new_row["golejador"] = accio[2]
                            if len(accio) == 5:
                                new_row["assistent"] = accio[4]
                            new_row["gol CF"] = True
                        else:
                            new_row["golejador"] = ""
                            new_row["assistent"] = ""
                            new_row["gol CF"] = False

                        players_in_equip = {player: True if player in equip else False for player in players}
                        new_row.update(players_in_equip)
                        GOLS = pd.concat((GOLS, pd.DataFrame([new_row])))
                    else:

                        accio = accio.split(" ")
                        minut_canvi = accio[0].split(".")
                        minut_canvi = timedelta(minutes=int(minut_canvi[0]), seconds=int(minut_canvi[1]))
                        surt = accio[1]
                        entra = accio[2]
                        
                        dif_temps = player_times[surt] - minut_canvi

                        player_times2[surt] += dif_temps
                        
                        player_times[entra] = minut_canvi
                        print("Surt:",surt)
                        print("Entra:",entra)
                        equip.remove(surt)
                        equip += [entra]

                        new_row = {"minut": minut_canvi,
                                    "part": p, 
                                    "dia partit": dia_partit}
                        players_in_equip = {player: True if player in equip else False for player in players}
                        new_row.update(players_in_equip)
                        CANVIS = pd.concat((CANVIS, pd.DataFrame([new_row])))
                    
                for jugador in equip:
                    player_times2[jugador] += player_times[jugador]
                
                for jugador, temps in player_times2.items():
                    if temps != 0:
                        new_row = {"jugador": jugador, "Minuts jugats": temps, 
                                "part": p , "dia partit": dia_partit}
                        MINUTS_JUGATS = pd.concat((MINUTS_JUGATS, pd.DataFrame([new_row])))
                        
                        """new_row = {"minut": minut_canvi,
                                    "part": p, 
                                    "dia partit": dia_partit}
                        players_in_equip = {player: True if player in equip else False for player in players}
                        new_row.update(players_in_equip)
                        CANVIS = pd.concat((CANVIS, pd.DataFrame([new_row])))"""

    stats = MINUTS_JUGATS.groupby("jugador").sum().drop(columns="part")

    for ind in list(stats.index):
        stats.loc[ind, "Gols"] = len(GOLS[GOLS["golejador"]==ind])
        stats.loc[ind, "Assistències"] = len(GOLS[GOLS["assistent"]==ind])
        stats.loc[ind, "Gols a favor estant a pista"] = len(GOLS[(GOLS[ind]==True) & (GOLS["gol CF"]==True)])
        stats.loc[ind, "Gols en contra estant a pista"] = len(GOLS[(GOLS[ind]==True) & (GOLS["gol CF"]==False)])

    stats['Minuts jugats'] = stats['Minuts jugats'].apply(lambda x: x.total_seconds() / 60.0)
    stats["Minuts/gols"] = stats["Minuts jugats"] / stats["Gols"]
    stats["Minuts/assistències"] = stats["Minuts jugats"] / stats["Assistències"]
    stats["Minuts/gols a favor estant a pista"] = stats["Minuts jugats"] / stats["Gols a favor estant a pista"]
    stats["Minuts/gols en contra estant a pista"] = stats["Minuts jugats"] / stats["Gols en contra estant a pista"]
    stats[stats.columns] = stats[stats.columns].round(2)

    stats = stats.drop(index=["coco", "corts"])
    stats = stats.reset_index()

    fig_gols = px.bar(stats.sort_values(by='Minuts/gols',  ascending=True), x='jugador', y='Minuts/gols', title='Minuts/gol')

    #fig_gols.show()

    fig_gols = px.bar(stats.sort_values(by='Minuts/assistències',  ascending=True), x='jugador', y='Minuts/assistències', title='Minuts/assistència')
    #fig_gols.show()

    # Crear un gràfic de barres per mostrar els minuts/gols a favor estant a pista per jugador
    fig_minuts_gols_a_pista = px.bar(stats.sort_values(by='Minuts/gols a favor estant a pista', ascending=True), x='jugador', y='Minuts/gols a favor estant a pista', title='Minuts/Gols a favor estant a Pista per Jugador')
    #fig_minuts_gols_a_pista.show()

    # Crear un gràfic de barres per mostrar els minuts/gols a favor estant a pista per jugador
    fig_minuts_gols_a_pista = px.bar(stats.sort_values(by='Minuts/gols en contra estant a pista',  ascending=False), x='jugador', y='Minuts/gols en contra estant a pista', title='Minuts/Gols en contra estant a Pista per Jugador')
    #fig_minuts_gols_a_pista.show()

    fig_minuts_gols_a_pista = px.scatter(stats, x='Minuts/gols a favor estant a pista', y='Minuts/gols en contra estant a pista', text='jugador', title='Rendiment')


    import plotly.subplots as sp
    import plotly.graph_objs as go

    # Create subplots
    fig = sp.make_subplots(rows=4, cols=2, specs=[[{}, {}], [{}, {}],
            [{"colspan": 2}, None], [{}, {}]], 
            subplot_titles=("Cada quants minuts fan un gol?", 
                            "Cada quants minuts fan una assistència?", 
                            "Cada quants minuts es fa un gol amb ell a pista", 
                            "Cada quants minuts ens fan un gol amb ell a pista",
                            "Rendiment",
                            "Cada quants minuts es fa un gol amb ells a pista",
                            "Cada quants minuts ens fan un gol amb ells a pista"))

    # Sort and create bar charts
    sorted_stats_gols = stats.sort_values(by='Minuts/gols', ascending=True)
    trace1 = go.Bar(x=sorted_stats_gols['jugador'], y=sorted_stats_gols['Minuts/gols'], text=sorted_stats_gols['Minuts/gols'], name='Minuts/gols', textfont=dict(color='white'))
    fig.add_trace(trace1, row=1, col=1)

    sorted_stats_assistencies = stats.sort_values(by='Minuts/assistències', ascending=True)
    trace2 = go.Bar(x=sorted_stats_assistencies['jugador'], y=sorted_stats_assistencies['Minuts/assistències'], text=sorted_stats_assistencies['Minuts/assistències'], name='Minuts/assistències', textfont=dict(color='white'))
    fig.add_trace(trace2, row=1, col=2)

    sorted_stats_gols_a_pista = stats.sort_values(by='Minuts/gols a favor estant a pista', ascending=True)
    trace3 = go.Bar(x=sorted_stats_gols_a_pista['jugador'], y=sorted_stats_gols_a_pista['Minuts/gols a favor estant a pista'], text=sorted_stats_gols_a_pista['Minuts/gols a favor estant a pista'], name='Minuts/Gols a favor estant a Pista', textfont=dict(color='white'))
    fig.add_trace(trace3, row=2, col=1)

    sorted_stats_gols_en_contra_a_pista = stats.sort_values(by='Minuts/gols en contra estant a pista', ascending=False)
    trace4 = go.Bar(x=sorted_stats_gols_en_contra_a_pista['jugador'], y=sorted_stats_gols_en_contra_a_pista['Minuts/gols en contra estant a pista'], text=sorted_stats_gols_en_contra_a_pista['Minuts/gols en contra estant a pista'], name='Minuts/Gols en contra estant a Pista', textfont=dict(color='white'))
    fig.add_trace(trace4, row=2, col=2)

    scatter_trace = go.Scatter(
        x=stats['Minuts/gols a favor estant a pista'],
        y=stats['Minuts/gols en contra estant a pista'],
        text=stats['jugador'],
        mode='markers+text',
        marker=dict(size=10),
        textposition='middle right',
        name='Rendiment'
    )

    fig.add_trace(scatter_trace, row=3, col =1)

    # Customize layout
    fig.update_layout(
        title="Anàlisi dels partits Castellfollit FS",
        showlegend=False,
        height=1400,    
        width=1400,
    )

    # Update x-axis titles

    fig.update_xaxes(title_text="Jugador", row=1, col=1)
    fig.update_xaxes(title_text="Jugador", row=1, col=2)
    fig.update_xaxes(title_text="Jugador", row=2, col=1)
    fig.update_xaxes(title_text="Jugador", row=2, col=2)
    fig.update_xaxes(autorange="reversed", title_text="Minuts/Gols a favor estant a Pista", row=3, col=1)

    # Update y-axis titles
    fig.update_yaxes(title_text="Minuts/gols", row=1, col=1)
    fig.update_yaxes(title_text="Minuts/assistències", row=1, col=2)
    fig.update_yaxes(title_text="Minuts/Gols a favor estant a Pista", row=2, col=1)
    fig.update_yaxes(title_text="Minuts/Gols en contra estant a Pista", row=2, col=2)
    fig.update_yaxes(title_text="Minuts/Gols en contra estant a Pista", row=3, col=1)

    # Update font and title font
    fig.update_layout(
        font=dict(family="Arial", size=12),
        title_font=dict(family="Arial", size=24),
    )


    COMBINACIONS_A_FAVOR = []
    COMBINACIONS_EN_CONTRA = []


    for index, row in GOLS[GOLS["gol CF"] == True][players].drop(columns=["coco", "corts"]).iterrows():
        COMBINACIONS_A_FAVOR.append([k for k, v in dict(row).items() if v == True])
    for index, row in GOLS[GOLS["gol CF"] == False][players].drop(columns=["coco", "corts"]).iterrows():
        COMBINACIONS_EN_CONTRA.append([k for k, v in dict(row).items() if v == True])

    from collections import Counter
    from itertools import combinations

    combinacions_a_favor = Counter()
    for comb in COMBINACIONS_A_FAVOR:
        for r in range(1, len(comb)+1):
            combos=combinations(comb, r)
            combinacions_a_favor.update(combos)

    combinacions_en_contra = Counter()
    for comb in COMBINACIONS_EN_CONTRA:
        for r in range(1, len(comb)+1):
            combos=combinations(comb, r)
            combinacions_en_contra.update(combos)

    CANVIS["minuts"] = CANVIS["minut"] - CANVIS["minut"].shift(-1)
    CANVIS[CANVIS["minuts"]<timedelta(seconds=0)]["minuts"] = CANVIS[CANVIS["minuts"]<timedelta(minutes=0)]["minut"]
    CANVIS = CANVIS.reset_index(drop=True)

    for part in range(2):
        CANVIS.loc[CANVIS[CANVIS["part"]==part].index[-1], "minuts"] = CANVIS.loc[CANVIS[CANVIS["part"]==part].index[-1], "minut"]

    comb_a_favor = {}
    for key, value in dict(combinacions_a_favor).items():

        res = {}
        res["gols"] = value

        temp = CANVIS.copy()
        for el in key:
            temp = temp[temp[el]==True]
        minuts = temp["minuts"].sum()
        res["minuts"] = minuts
        res["minuts/gols"] = minuts/value
        comb_a_favor[key] = res

    def convert_timedelta_to_seconds(data_item):
        return data_item[1]['minuts/gols'].total_seconds()

    sorted_data = dict(sorted(comb_a_favor.items(), key=convert_timedelta_to_seconds))

    l_c = [(labels, counts["minuts/gols"]) for (labels, counts) in sorted_data.items()][:10]
    labels = [l[0] for l in l_c]
    counts = [c[1].total_seconds() / 60.0 for c in l_c]
    labels=[str(list((l))) for l in labels]
    trace3 = go.Bar(x=labels, y=counts)
    fig.add_trace(trace3, row=4, col=2)
    fig.update_xaxes(tickangle=45, row=4, col=2)
    fig.update_xaxes(title_text="Jugador", row=4, col=2)
    fig.update_yaxes(title_text="Minuts/Gols a favor estant a Pista", row=4, col=2)

    comb_en_contra = {}
    for key, value in dict(combinacions_en_contra).items():

        res = {}
        res["gols"] = value

        temp = CANVIS.copy()
        for el in key:
            temp = temp[temp[el]==True]
        minuts = temp["minuts"].sum()
        res["minuts"] = minuts
        res["minuts/gols"] = minuts/value
        comb_en_contra[key] = res

    def convert_timedelta_to_seconds(data_item):
        return data_item[1]['minuts/gols'].total_seconds()

    sorted_data = dict(sorted(comb_en_contra.items(), key=convert_timedelta_to_seconds))

    l_c = [(labels, counts["minuts/gols"]) for (labels, counts) in sorted_data.items()][:10]
    labels = [l[0] for l in l_c]
    counts = [c[1].total_seconds() / 60.0 for c in l_c]
    labels=[str(list((l))) for l in labels]
    trace3 = go.Bar(x=labels, y=counts)
    fig.add_trace(trace3, row=4, col=1)
    fig.update_xaxes(tickangle=45, row=4, col=1)
    fig.update_xaxes(title_text="Jugador", row=4, col=1)
    fig.update_yaxes(title_text="Minuts/Gols en contra estant a Pista", row=4, col=1)

    stats2 = stats.copy()

    jugador = "piu"
    titles = ["Minuts/gols en contra estant a pista", "Minuts jugats"]
    titles2 = ["Minuts/gols a favor estant a pista", "Minuts/gols", "Minuts/assistències"]

    stats2.loc[stats2["Minuts/gols"] == np.inf, "Minuts/gols"] = np.nan
    stats2.loc[stats2["Minuts/assistències"] == np.inf, "Minuts/assistències"] = np.nan

    stats3 = stats2[titles+titles2+["jugador"]]
    stats3 = stats3.melt(id_vars=["jugador"], var_name="variable", value_name="value")

    #valor_escalado = (valor - inicio_rango_inicial) * (fin_rango_destino - inicio_rango_destino) / (fin_rango_inicial - inicio_rango_inicial) + inicio_rango_destino
    #start2 + (stop2 - start2) * (stop1 - value) / (stop1 - start1)

    stats2[titles] = (stats2[titles] - stats2[titles].min()) * (1 - 0.3)/(stats2[titles].max() - stats2[titles].min())+0.3

    for col in titles2:
        stats2[col] = 0.3 + (1- 0.3) * (stats2[col].max() -stats2[col])/(stats2[col].max() - 0.3)

    stats2 = stats2.fillna(0)

    df2 = stats2[titles+titles2+["jugador"]]
    df2 = df2.melt(id_vars=["jugador"], var_name="variable", value_name="relative value")

    df2["real value"] = stats3["value"]

    fig2 = px.line_polar(df2, r="relative value", theta="variable", line_close=True, color="jugador",hover_data=["real value"])
    fig2.update_traces(showlegend=True, selector=dict(name="jugador"))

    fig2.update_layout(
        title = "Coparativa entre estadísiques",
        height=500,    
        width=1400)
    
    return fig2
