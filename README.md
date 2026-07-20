# 📊 Customer Feedback Dashboard

An interactive dashboard that analyzes customer feedback sentiment using **TextBlob**,
and visualizes the results with **Plotly**, all served through **Streamlit**.
<img width="1920" height="1080" alt="Screenshot (1)" src="https://github.com/user-attachments/assets/62f235c6-fbd9-406a-b83f-3dd0b68ad28a" />
<img width="1920" height="1080" alt="Screenshot (2)" src="https://github.com/user-attachments/assets/90db4226-2c10-4038-afa7-0d41dc8da897" />


## Features
- Upload your own CSV or use the bundled sample dataset
- Automatic sentiment analysis (Positive / Neutral / Negative) + polarity & subjectivity scores
- KPI cards: total feedback, % positive/neutral/negative, average rating
- Sentiment distribution pie chart
- Polarity score histogram
- Sentiment trend over time (line chart)
- Rating vs. sentiment polarity scatter plot
- Sentiment breakdown by product (stacked bar chart)
- Top 5 most positive / most negative feedback highlights
- Filterable, sortable data table + CSV export of analyzed results

## Project Structure
```
customer-feedback-dashboard/
├── app.py                    # Main Streamlit application
├── requirements.txt           # Python dependencies
├── data/
│   └── sample_feedback.csv    # Sample dataset (30 rows)
└── README.md                  # This file
```

## Prerequisites
- Python 3.9+ installed
- VS Code (with the Python extension) installed

## Setup & Run — Step by Step (VS Code)

### 1. Unzip and open the project
Unzip `customer-feedback-dashboard.zip` anywhere on your machine, then in VS Code:
`File → Open Folder...` → select the `customer-feedback-dashboard` folder.

### 2. Open a terminal in VS Code
`Terminal → New Terminal` (or `` Ctrl+` ``).

### 3. Create a virtual environment (recommended)
```bash
python -m venv venv
```
Activate it:
- **Windows:** `venv\Scripts\activate`
- **macOS/Linux:** `source venv/bin/activate`

VS Code may prompt "Select Interpreter" — choose the one inside `venv`.

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Download TextBlob's language corpora (one-time step)
TextBlob needs NLTK corpora for sentiment analysis:
```bash
python -m textblob.download_corpora
```

### 6. Run the app
```bash
streamlit run app.py
```

### 7. View it in your browser
Streamlit will automatically open a browser tab. If not, go to:
```
http://localhost:8501
```

You should now see the full dashboard running locally, pre-loaded with the sample dataset.

## Using Your Own Data
Upload any CSV via the sidebar. At minimum it needs one text column (e.g. `feedback_text`).
Optional columns that unlock extra charts:
- `date` → enables the sentiment trend chart
- `rating` → enables the rating vs. sentiment scatter plot and average-rating KPI
- `product` → enables the per-product sentiment breakdown

## Troubleshooting
- **"streamlit: command not found"** → make sure your virtual environment is activated.
- **TextBlob corpora errors** (e.g. `Resource punkt not found`) → re-run step 5.
- **Port 8501 already in use** → run `streamlit run app.py --server.port 8502` and open `http://localhost:8502`.
- **Blank charts** → check your CSV column names match what's expected, or reselect the correct text column in the sidebar.

## Stopping the App
Go back to the VS Code terminal and press `Ctrl+C`.
