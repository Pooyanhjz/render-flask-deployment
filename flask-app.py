from flask import Flask
import pandas as pd
import easygui

app = Flask(__name__)

@app.route("/", methods=['GET'])
def filter_dataset():
    # Load dataset
    file_path = easygui.fileopenbox(title="Select your dataset CSV file")
    df = pd.read_csv(file_path)

    #Fill the empty value of statoEsteroStudioLavoro with Italia
    df["statoEsteroStudioLavoro"] = df["statoEsteroStudioLavoro"].fillna("Italia")

    # Add a new column "nome_di_mezzo" based on the "mezzo" column
    mezzo_mapping = {
        1: "treno",
        2: "tram",
        3: "metropolitana",
        4: "autobus urbano, filobus",
        5: "corriera, autobus extra-urbano",
        6: "autobus aziendale o scolastico",
        7: "auto privata (come conducente)",
        8: "auto privata (come passeggero)",
        9: "motocicletta, ciclomotore, scooter",
        10: "bicicletta",
        11: "altro mezzo",
        12: "a piedi"
    }
    df["nome_di_mezzo"] = df["mezzo"].map(mezzo_mapping)
    
    # Add a new column "nome_di_motivo_spostamento" based on the "motivoSpostamento" column
    motivo_mapping = {
        1: "si reca al luogo di studio",
        2: "si reca al luogo di lavoro"
    }
    df["nome_di_motivo_spostamento"] = df["motivoSpostamento"].map(motivo_mapping)

    def multi_select(prompt, options, allow_all=True):
        choices = easygui.multchoicebox(prompt, "Selection", options)
        if allow_all and choices is None:
            return options
        return choices

    # User selection for Residenza
    regioni_res = df['regioneResidenza'].unique().tolist()
    selected_regioni_res = multi_select("Select region(s) of residence:", regioni_res)

    province_res = df[df['regioneResidenza'].isin(selected_regioni_res)]['provinciaResidenza'].unique().tolist()
    selected_province_res = multi_select("Select province(s) of residence:", province_res)

    comuni_res = df[df['provinciaResidenza'].isin(selected_province_res)]['comuneResidenza'].unique().tolist()
    selected_comuni_res = multi_select("Select comune(s) of residence:", comuni_res)

    regioni_sl = df['regioneSL'].unique().tolist()
    selected_regioni_sl = multi_select("Select region(s) of study/work:", regioni_sl)

    province_sl = df[df['regioneSL'].isin(selected_regioni_sl)]['provinciaSL'].unique().tolist()
    selected_province_sl = multi_select("Select province(s) of study/work:", province_sl)

    comuni_sl = df[df['provinciaSL'].isin(selected_province_sl)]['comuneSL'].unique().tolist()
    selected_comuni_sl = multi_select("Select comune(s) of study/work:", comuni_sl)

    transport_options = [
        "1 treno", "2 tram", "3 metropolitana", "4 autobus urbano, filobus", "5 corriera, autobus extra-urbano", 
        "6 autobus aziendale o scolastico", "7 auto privata (come conducente)", "8 auto privata (come passeggero)",
        "9 motocicletta, ciclomotore, scooter", "10 bicicletta", "11 altro mezzo", "12 a piedi"
    ]
    selected_transport = multi_select("Select means of transport:", transport_options)

    reason_options = ["1 si reca al luogo di studio", "2 si reca al luogo di lavoro"]
    selected_reason = multi_select("Select reason for travel:", reason_options)

    country = df["statoEsteroStudioLavoro"].unique().tolist()
    selected_country = multi_select("Select the country", country)

    filtered_df = df[
        df['regioneResidenza'].isin(selected_regioni_res) &
        df['provinciaResidenza'].isin(selected_province_res) &
        df['comuneResidenza'].isin(selected_comuni_res) &
        df['regioneSL'].isin(selected_regioni_sl) &
        df['provinciaSL'].isin(selected_province_sl) &
        df['comuneSL'].isin(selected_comuni_sl) &
        df['mezzo'].isin([int(t.split()[0]) for t in selected_transport]) &
        df['motivoSpostamento'].isin([int(r.split()[0]) for r in selected_reason]) &
        df["statoEsteroStudioLavoro"].isin(selected_country)
    ]

    return filtered_df

# Main loop to run filter_dataset repeatedly
all_filtered_data = pd.DataFrame()  # Container to hold all concatenated results

while easygui.ynbox("Do you want to filter a new dataset?", "New Dataset Filter"):
    new_data = filter_dataset()
    all_filtered_data = pd.concat([all_filtered_data, new_data], ignore_index=True)

# Ask the user if they want to save the final dataset to a CSV file
if easygui.ynbox("Do you want to save the final concatenated dataset to a CSV file?", "Save to CSV"):
    file_path = easygui.filesavebox("Enter the file name and choose location", default="", filetypes=["*.csv"])
    if file_path:
        # Automatically add the .csv extension if it's not present
        if not file_path.lower().endswith(".csv"):
            file_path += ".csv"
        all_filtered_data.to_csv(file_path, index=False)
        easygui.msgbox("Dataset saved successfully!")

if __name__ == "__main__":
    app.run()