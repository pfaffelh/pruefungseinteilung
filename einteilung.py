import os as os
import csv, ast
import pandas as pd
import numpy as np
from datetime import datetime
from scipy.optimize import linear_sum_assignment
import jinja2
import os
from jinja2 import Template

latex_jinja_env = jinja2.Environment(
    block_start_string = '\BLOCK{',
    block_end_string = '}',
    variable_start_string = '\VAR{',
    variable_end_string = '}',
    comment_start_string = '\#{',
    comment_end_string = '}',
    line_statement_prefix = '%%',
    line_comment_prefix = '%#',
    trim_blocks = True,
    autoescape = False,
    loader = jinja2.FileSystemLoader(os.path.abspath('.'))
)

def get_anmeldungen_from_hisinone(anmeldungen_from_hisinone_csv, prüfungsnummern_csv):
    anmeldungen_hisinone = pd.read_csv(anmeldungen_from_hisinone_csv)
    anmeldungen_hisinone['id_hisinone'] = anmeldungen_hisinone.index
    anmeldungen_hisinone.set_index('id_hisinone')
#    anmeldungen_hisinone = anmeldungen_hisinone.drop(labels = ['Titel', 'Akademischer Grad', 'Geschlecht'], axis=1)
    anmeldungen_hisinone['Fach'] = ""
    anmeldungen_hisinone['Studiengang'] = ""
    prüfungsnummern = pd.read_csv(prüfungsnummern_csv)
    studiengang_dict = dict(zip(prüfungsnummern['Nummer'], prüfungsnummern['Studiengang'])) 
    fach_dict = dict(zip(prüfungsnummern['Nummer'], prüfungsnummern['Fach'])) 
    for index, row in anmeldungen_hisinone.iterrows():
        loc = row["Nummer"].split("-")
        anmeldungen_hisinone.at[index, 'Studiengang'] = studiengang_dict[row['Nummer']]
        anmeldungen_hisinone.at[index, 'Fach'] = fach_dict[row['Nummer']]

    anmeldungen_hisinone = anmeldungen_hisinone.drop(labels = ['Nummer'], axis=1)
    anmeldungen_hisinone = anmeldungen_hisinone[['id_hisinone', 'Nachname', 'Vorname', 'Matrikelnummer', 'Fach', 'Studiengang']]
    anmeldungen_hisinone.sort_values(by=['Matrikelnummer', 'Fach'], inplace=True)
    print(f"{len(anmeldungen_hisinone)} Anmeldungen erfolgreich eingelesen.")
    return anmeldungen_hisinone


# This function is used when converting the www_anmeldungen:
def compute_fach_from_studiengang_pruefung(df_row):
    fach = ""
    if((df_row['studiengang'] == "lehramt") & (df_row['pruefung'] == "analysis")):
        fach = "Analysis I+II"
    elif ((df_row['studiengang'] == "bachelor") & (df_row['pruefung'] == "analysis")):
        fach = "Analysis I-III"
    elif (df_row['pruefung'] == "linalg"):
        fach = "Lineare Algebra"
    return fach

def get_anmeldungen_from_www(anmeldungen_www_folder):
    anmeldungen_www = pd.DataFrame()
    # get rid of all files with non-digit names
    filelist = [file for file in os.listdir(anmeldungen_www_folder) if file.isdigit()]

    for file in filelist:
        with open(f'{anmeldungen_www_folder}/{file}', 'r') as f:
            txt = f.read()
            dct = ast.literal_eval(txt)
            df_loc = pd.DataFrame([dct])
            anmeldungen_www = pd.concat([anmeldungen_www, df_loc])
    anmeldungen_www['id_www'] = [int(i) for i in filelist]

    anmeldungen_www.rename(columns = {'vorname':'Vorname', 'nachname':'Nachname', 'matrnr':'Matrikelnummer'}, inplace = True)

    anmeldungen_www['Fach'] = anmeldungen_www.apply(compute_fach_from_studiengang_pruefung, axis=1)
    anmeldungen_www = anmeldungen_www.drop(labels = ['studiengang', 'pruefung'], axis=1)
    column_names = ['id_www', 'Nachname', 'Vorname', 'Matrikelnummer', 'Fach', 'wunsch1', 'wunsch2', 'wunsch3']
    anmeldungen_www = anmeldungen_www[column_names]

    anmeldungen_www.sort_values(by=['Matrikelnummer', 'Fach', 'id_www'], inplace=True)
    anmeldungen_www.reset_index(inplace=True, drop=True)
    print(f"{len(anmeldungen_www)} Anmeldungen erfolgreich eingelesen.")
    return anmeldungen_www

def compare_anmeldungen_hisinone_www(anmeldungen_hisinone_csv, anmeldungen_www_ohne_duplikate_csv):
    # Einlesen der csv's als Dataframe
    anmeldungen_hisinone = pd.read_csv(anmeldungen_hisinone_csv)
    anmeldungen_www_ohne_duplikate = pd.read_csv(anmeldungen_www_ohne_duplikate_csv)

#    print(anmeldungen_hisinone.head())
#    print(anmeldungen_www_ohne_duplikate.head())
    # Vergleich der Einträge
    # Zuerst die, die in HisInOne angemeldet sind, aber keine Wünsche angegeben haben.
    common = anmeldungen_hisinone.merge(anmeldungen_www_ohne_duplikate, on=['Vorname','Nachname', 'Matrikelnummer', 'Fach'])
    anmeldungen_hisinone_notwww = anmeldungen_hisinone.drop([i for i in range(len(anmeldungen_hisinone)) if anmeldungen_hisinone['id_hisinone'].iloc[i] in common['id_hisinone'].iloc])

    if(len(anmeldungen_hisinone_notwww)==0):
        print("Alle Anmeldungen in HisInOne haben einen Prüferwunsch abgegeben!")
    else:
        print("Anmeldungen in HisInOne, die keine Prüferwünsche angegebene haben:")
        print(anmeldungen_hisinone_notwww)

    print("\n")

    common = anmeldungen_www_ohne_duplikate.merge(anmeldungen_hisinone, on=['Vorname','Nachname', 'Matrikelnummer', 'Fach'])
    anmeldungen_www_nothisinone = anmeldungen_www_ohne_duplikate.drop([i for i in range(len(anmeldungen_www_ohne_duplikate)) if anmeldungen_www_ohne_duplikate['id_www'].iloc[i] in common['id_www'].iloc])

    if(len(anmeldungen_www_nothisinone.index)==0):
        print("Alle Prüflinge, die einen Prüferwunsch abgegeben haben, haben sich auf HisInOne ebenfalls angemeldet!")
    else:
        print("Anmeldungen, die einen Prüferwunsch angegeben haben, aber nicht in HisInOne erscheinen:")
        print(anmeldungen_www_nothisinone)

def get_zuordnungen_from_df(prüferwünsche, anmeldungen_hisinone, anmeldungen_www_ohne_duplikate, weights):
    spalten = []
    for index,prüfer in prüferwünsche.iterrows():
        spalten.extend([prüfer['Kurzname'] for i in range(prüfer['Prüfungszahl'])])
    kosten = np.zeros((len(anmeldungen_hisinone), len(spalten)))

    prüferliste = {
        key : [prüferwünsche['Kurzname'].iloc[k] for k in range(len(prüferwünsche)) if prüferwünsche[key].iloc[k] == 1] for key in ['Analysis I+II', 'Analysis I-III', 'Lineare Algebra']
    }
    
    for i in range(kosten.shape[0]):
        for j in range(kosten.shape[1]):
            if(anmeldungen_hisinone['wunsch1'].iloc[i] == spalten[j]):
                kosten[i,j] = float(weights[0])  if spalten[j] in prüferliste[anmeldungen_hisinone['Fach'].iloc[i]] else float(weights[4])  
            elif(anmeldungen_hisinone['wunsch2'].iloc[i] == spalten[j]):
                kosten[i,j] = float(weights[1])  if spalten[j] in prüferliste[anmeldungen_hisinone['Fach'].iloc[i]] else float(weights[4]) 
            elif(anmeldungen_hisinone['wunsch3'].iloc[i] == spalten[j]):
                kosten[i,j] = float(weights[2])  if spalten[j] in prüferliste[anmeldungen_hisinone['Fach'].iloc[i]] else float(weights[4])
            else: 
                kosten[i,j] = float(weights[3]) if spalten[j] in prüferliste[anmeldungen_hisinone['Fach'].iloc[i]] else float(weights[4])
    row_ind, col_ind = linear_sum_assignment(kosten, maximize=False)
#    print(f"Gesamtkosten {kosten[row_ind, col_ind].sum()}")
    prüfer = [spalten[j] for j in col_ind]
    anmeldungen_hisinone['Prüfer'] = prüfer
    anmeldungen_hisinone = anmeldungen_hisinone.sort_values(by = ['Prüfer', 'Fach']).reset_index(drop=True)
#    print(anmeldungen_hisinone.head())
    anmeldungen_hisinone['prüfungs_id'] = anmeldungen_hisinone.index
#    print(anmeldungen_hisinone.head())
    anmeldungen_hisinone.set_index('prüfungs_id')
    zuordnungen = anmeldungen_hisinone[['prüfungs_id', 'Nachname', 'Vorname', 'Matrikelnummer', 'Studiengang', 'Fach', 'Prüfer', 'wunsch1', 'wunsch2', 'wunsch3', 'id_hisinone', 'id_www']]
    return zuordnungen, kosten, row_ind, col_ind
        
    
from IPython.display import clear_output

def get_zuordnungen(prüferwünsche_csv, anmeldungen_hisinone_csv, anmeldungen_www_ohne_duplikate_csv, weights, max_iterations, max_malus):
    prüferwünsche = pd.read_csv(prüferwünsche_csv)
    anmeldungen_hisinone = pd.read_csv(anmeldungen_hisinone_csv)
    anmeldungen_www_ohne_duplikate = pd.read_csv(anmeldungen_www_ohne_duplikate_csv)

    prüferwünsche['Prüfungszahl'] = prüferwünsche['Prüfungszahl'].astype('int')
    
    # merge, so dass die Wünsche auch in anmeldungen_hisinone stehen
    anmeldungen_hisinone = anmeldungen_hisinone.merge(anmeldungen_www_ohne_duplikate, how='left', on=['Vorname','Nachname', 'Matrikelnummer', 'Fach'])
#    print(anmeldungen_hisinone.head())
    # In der Gewichts-Matrix sind nun die Zeilen die Prüflinge aus anmeldungen_hisinone, die Spalten sind
    # alle von den Prüfern angebotenen Prüfungen. An der Stelle i, j in der Matrix stehen die Kosten, Prüfling
    # i zu Prüfer j einzuteilen. Die Matrix wird zu 10 initialisiert. Hat ein Prüfling einen Wunsch abgegeben,
    # so verringert das die Kosten bei wunsch1-3.
    zuordnungen, kosten, row_ind, col_ind = get_zuordnungen_from_df(prüferwünsche, anmeldungen_hisinone, anmeldungen_www_ohne_duplikate, weights)
    gesamtkosten = kosten[row_ind, col_ind].sum()
    zuordnungen_alt, gesamtkosten_alt = zuordnungen, gesamtkosten
    gesamtkosten_init = gesamtkosten_alt
    pd.options.mode.chained_assignment = None 
    iterations = 0
    while(iterations < max_iterations and gesamtkosten <= gesamtkosten_init + max_malus and (kosten.shape[1] > kosten.shape[0])):
        iterations += 1
        print(f"Iteration {iterations}")
        zuordnungen_alt, gesamtkosten_alt = zuordnungen, gesamtkosten
        i = prüferwünsche['Prüfungszahl'].tolist().index(max(prüferwünsche['Prüfungszahl'].tolist()))
        prüferwünsche['Prüfungszahl'].iloc[i] = max(prüferwünsche['Prüfungszahl'].tolist()) - 1
        zuordnungen, kosten, row_ind, col_ind = get_zuordnungen_from_df(prüferwünsche, anmeldungen_hisinone, anmeldungen_www_ohne_duplikate, weights)
        gesamtkosten = kosten[row_ind, col_ind].sum()
        if(gesamtkosten > gesamtkosten_alt and gesamtkosten <= gesamtkosten_init + max_malus):
            print(f"Warning: Gesamtkosten sind um {gesamtkosten - gesamtkosten_alt} gestiegen!")
        clear_output(wait=True)
    if(max_iterations > 0):
        print(f"Gesamtkosten am Anfang: {gesamtkosten_init}")
        print(f"Iterations: {iterations}\n")
    return zuordnungen_alt, gesamtkosten_alt


def get_statistiken_from_zuordnungen(zuordnungen_csv, prüferwünsche_csv):
    zuordnungen = pd.read_csv(zuordnungen_csv)
    prüferwünsche = pd.read_csv(prüferwünsche_csv)
    print(f"\nGesamtzahl an zugeordneten Prüfungen: {len(zuordnungen)}\n")
    print(f"Anzahl Prüflinge ohne Prüferwünsche:  {len([i for i in zuordnungen['wunsch1'] if pd.isnull(i)])}")
    print(f"Anzahl Prüflinge bei wunsch1:         {len([i for i in zuordnungen['wunsch1'].index if zuordnungen['wunsch1'].iloc[i] == zuordnungen['Prüfer'].iloc[i]])}")
    print(f"Anzahl Prüflinge bei wunsch2:         {len([i for i in zuordnungen['wunsch1'].index if zuordnungen['wunsch2'].iloc[i] == zuordnungen['Prüfer'].iloc[i]])}")
    print(f"Anzahl Prüflinge bei wunsch3:         {len([i for i in zuordnungen['wunsch1'].index if zuordnungen['wunsch3'].iloc[i] == zuordnungen['Prüfer'].iloc[i]])}\n")
    for index, prüfer in prüferwünsche.iterrows():
        print(f"Prüfungen bei {prüfer['Kurzname']}: {len([i for i in zuordnungen['Prüfer'].index if prüfer['Kurzname'] == zuordnungen['Prüfer'].iloc[i]])} (von {prüfer['Prüfungszahl']})")
#    print(zuordnungen)
    
    

def check_prüferwünsche_und_slots(prüferwünsche_csv, zuordnungen_csv, prüfungsslots_csv):
    prüferwünsche = pd.read_csv(prüferwünsche_csv)
    prüfungsslots = pd.read_csv(prüfungsslots_csv)
    zuordnungen = pd.read_csv(zuordnungen_csv)
    prüfer_list = prüferwünsche['Kurzname'].tolist()
    prüfungszahl_list = [int(i) for i in prüferwünsche['Prüfungszahl']]
    prüfungszahl_from_zuordnungen = zuordnungen['Prüfer'].value_counts()
    prüfungszahl_from_prüfungsslots = prüfungsslots['Kurzname'].value_counts()
    prüfungszahl_from_prüferwünsche = dict(zip(prüferwünsche['Kurzname'], prüferwünsche['Prüfungszahl']))

    error = False
    for prüfer in prüfer_list:
#        if prüfungszahl_from_prüfungsslots.get(prüfer, 0) > prüfungszahl_from_prüferwünsche.get(prüfer,0):
#            print(f"Warnung: Prüfer {prüfer} bietet mehr Slots an als in {prüferwünsche_csv} angegeben!")
        if prüfungszahl_from_zuordnungen.get(prüfer,0) > prüfungszahl_from_prüfungsslots.get(prüfer,0):
            print(f"Fehler: Prüfer {prüfer} hat nur {prüfungszahl_from_prüfungsslots.get(prüfer,0)} Prüfungsslots angegeben, muss aber {prüfungszahl_from_zuordnungen.get(prüfer,0)} Prüfungen abnehmen (siehe {zuordnungen_csv})!")
            error = True
    return error

def make_zuordnungen_zu_slots(prüfungsslots_csv, zuordnungen_csv):
    zuordnungen = pd.read_csv(zuordnungen_csv)
    prüfungsslots = pd.read_csv(prüfungsslots_csv).reset_index()
    prüfer_list = prüfungsslots.Kurzname.unique()
    prüfungs_ids_dict = {}
    prüfungsslots_dict = {}
    for prüfer in prüfer_list:
        prüfungs_ids_dict[prüfer] = [zuordnungen['prüfungs_id'].iloc[i] for i in zuordnungen.index if zuordnungen['Prüfer'].iloc[i] == prüfer]
        prüfungsslots_dict[prüfer] = [i for i in prüfungsslots.index if prüfungsslots['Kurzname'].iloc[i] == prüfer]
    prüfungs_ids = []
    for prüfer in prüfer_list:
        for i in range(len(prüfungsslots_dict[prüfer])):
            if i < len(prüfungs_ids_dict[prüfer]):
                prüfungs_ids.append(prüfungs_ids_dict[prüfer][i])
            else:
                prüfungs_ids.append('')
    prüfungsslots['prüfungs_id'] = prüfungs_ids
    return prüfungsslots.drop(labels='index', axis=1)


def make_prüfungsplan(prüfungsslots_mit_prüfungs_ids_csv, zuordnungen_csv, prüferwünsche_csv):
    prüfungsslots_mit_prüfungs_ids = pd.read_csv(prüfungsslots_mit_prüfungs_ids_csv).reset_index()
    zuordnungen = pd.read_csv(zuordnungen_csv)
    prüferwünsche = pd.read_csv(prüferwünsche_csv)

    # Lösche Zeilen aus prüfungsslots ohne Prüfung
    prüfungsslots_mit_prüfungs_ids.dropna(inplace = True)
    prüfungsslots_mit_prüfungs_ids['index'] = [int(x) for x in prüfungsslots_mit_prüfungs_ids['index']]

    # Überprüfe, ob beide Dateien dieselben Indizes (Prüfungen) beinhalten.
    loc = set(prüfungsslots_mit_prüfungs_ids['prüfungs_id']) - set(zuordnungen['prüfungs_id'])
    if loc != set():
        print(f"Indices {loc} sind in prüfungsslots_mit_prüfungs_ids, aber nicht in zuordnungen!")
    loc = set(zuordnungen['prüfungs_id']) - set(prüfungsslots_mit_prüfungs_ids['prüfungs_id'])
    if loc != set():
        print(f"Indices {loc} sind in zuordnungen, aber nicht in prüfungsslots_mit_prüfungs_ids!")

    # Merge beide Dataframes, um anschließend zu prüfen, ob beides derselbe Prüfer ist.
    prüfungsslots_mit_prüfungs_ids = prüfungsslots_mit_prüfungs_ids.merge(zuordnungen, on = ['prüfungs_id'])

    for index, row_prüfungsslots in prüfungsslots_mit_prüfungs_ids.iterrows():
        if row_prüfungsslots['Kurzname'] != row_prüfungsslots['Prüfer']:
            print("Fehler für folgende Zeile:")
            print(row_prüfungsslots)

    prüfer_vorname_dict = dict(zip(prüferwünsche['Kurzname'], prüferwünsche['Vorname']))
    prüfungsslots_mit_prüfungs_ids['Prüfer_Vorname'] = [prüfer_vorname_dict[x] for x in prüfungsslots_mit_prüfungs_ids['Kurzname']]

    prüfer_nachname_dict = dict(zip(prüferwünsche['Kurzname'], prüferwünsche['Nachname']))
    prüfungsslots_mit_prüfungs_ids['Prüfer_Nachname'] = [prüfer_nachname_dict[x] for x in prüfungsslots_mit_prüfungs_ids['Kurzname']]

#    fach = {"Ana12": "Analysis I+II", "Ana123": "Analysis I-III", "LA": "Lineare Algebra"}
#    prüfungsslots_mit_prüfungs_ids['Fach'] = [fach[x] for x in prüfungsslots_mit_prüfungs_ids['Fach']] 
    
#    prüfungsslots_mit_prüfungs_ids.drop(columns = ['Prüfer', 'Kurzname', 'index', 'prüfungs_id'], inplace = True)

    # Konvertiere Datum und Uhrzeit in ein Datetime-Objekt (zur späteren Sortierung)
    # print(["f{x[0]} {x[1]}" for x in prüfungsslots[['Datum', 'Uhrzeit']]])

    Prüfung_datetime = []
    for index, row_prüfungsslot in prüfungsslots_mit_prüfungs_ids.iterrows():
        Datum_Uhrzeit = f"{row_prüfungsslot['Datum']} {row_prüfungsslot['Uhrzeit']}"
        Prüfung_datetime.append(datetime.strptime(Datum_Uhrzeit, '%d.%m.%y %H:%M:%S'))

    prüfungsslots_mit_prüfungs_ids['Datetime'] = Prüfung_datetime
    prüfungsslots_mit_prüfungs_ids.sort_values(by = ['Kurzname','Datetime'], inplace=True)
    
    return prüfungsslots_mit_prüfungs_ids[['Prüfer_Nachname', 'Prüfer_Vorname', 'Datum', 'Uhrzeit', 'Raum', 'Fach', 
                               'Nachname', 'Vorname', 'Studiengang', 'Matrikelnummer']]

def make_3digit_string(i):
    res=""
    if(i<10):
        res = f"00{i}"
    elif(i<100):
        res = f"0{i}"
    else:
        res = f"{i}"
    return res



def make_niederschriften(prüfungsplan_csv, niederschriften_ordner, niederschriften_template_tex, latex_output, niederschiften_alle_pdf):
    if os.path.exists(niederschriften_ordner):
        os.system(f"rm -f {niederschriften_ordner}/*")
    else:
        os.system(f"mkdir {niederschriften_ordner}")
                  
    prüfungsplan = pd.read_csv(prüfungsplan_csv).reset_index()
    filenames_prefix = [f"{make_3digit_string(prüfungsplan['index'].iloc[i])}_{prüfungsplan['Prüfer_Nachname'].iloc[i].replace(' ', '')}_{prüfungsplan['Matrikelnummer'].iloc[i]}" for i in prüfungsplan.index]
#    print(filenames_prefix)
    template = latex_jinja_env.get_template(f"{niederschriften_template_tex}")
    for index, row_prüfungsplan in prüfungsplan.iterrows():
        document = template.render(prüfung = row_prüfungsplan)
#        print(f"{niederschriften_ordner}/{filenames_prefix[index]}.tex")
        with open(f"{niederschriften_ordner}/{filenames_prefix[index]}.tex",'w') as output:
             output.write(document)
    os.system(f"rm {latex_output}")
    os.chdir(f"{niederschriften_ordner}")
    for filename_prefix in filenames_prefix:
        print(f"Working on {filename_prefix}.tex")
        os.system(f"pdflatex -interaction=nonstopmode {filename_prefix}.tex >> ../{latex_output}")
        os.system(f"pdflatex -interaction=nonstopmode {filename_prefix}.tex >> ../{latex_output}")
        clear_output(wait=True)
    clear_output(wait=True)

    os.system(f"rm *.tex")
    os.system(f"rm *.aux")
    os.system(f"rm *.log")
    os.system(f"pdftk *.pdf cat output ../{niederschiften_alle_pdf}")
    os.chdir(f"..")
    print(f"Niederschriften sind im Ordner {niederschriften_ordner} und in {niederschiften_alle_pdf}")
