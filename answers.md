# MovieIQ Project Answers - Professional Analyst Report

## STAGE 0 Problem Statement
**1. In your own words, explain what makes a movie "successful" in this project. Write the exact rule you will use to label a movie as a success or a failure.**
For the scope of this baseline model, financial success is strictly defined by nominal profitability—when gross revenue strictly exceeds the reported production budget. 
Exact logic: `success = 1 if revenue > budget else 0`.
*Note: This is a highly reductive metric. It critically ignores Prints & Advertising (P&A) costs, inflation, theatrical revenue splits, and ancillary downstream revenues, heavily biasing the model toward false profitability.*

**2. Why is predicting film success valuable? Name two stakeholders (e.g. studios, investors) and how such a prediction could help them.**
The film industry is a high-risk venture characterized by non-normal, heavy-tailed return distributions (the "blockbuster" dynamic).
- **Studios/Production Companies:** Enables data-driven greenlighting processes and optimized capital allocation, shifting decision-making from subjective intuition to empirical risk assessment.
- **Institutional Investors/Financiers:** Provides a quantitative foundation for portfolio diversification and ROI probability forecasting before committing capital to production slates.

**3. State the objective of the project and list at least three concrete steps you will take to reach it.**
Objective: Engineer a supervised machine learning classification pipeline to predict binary film profitability and operationalize it via an interactive dashboard.
Steps:
1. **Data Preprocessing & Feature Engineering:** Execute rigorous data cleaning (handling missing/zero values) and parse unstructured JSON-like categorical arrays (genres) into actionable dummy variables.
2. **Exploratory Data Analysis (EDA) & Hypothesis Testing:** Identify statistically significant predictors of success using bivariate analysis, correlation matrices, and inferential statistics (T-tests, Chi-Square).
3. **Model Development & Deployment:** Train, tune, and evaluate a Random Forest Classifier to handle non-linear relationships, followed by deploying the inference engine via Streamlit.

**4. This is a classification problem. Explain what that means and what your model's target variable will be.**
Classification is a supervised learning paradigm where the objective is to map input features to a discrete, categorical output. We are not predicting the continuous revenue figure (which would be regression), but rather a binary state.
Target variable: `success` (Boolean/Binary: 1 for Success, 0 for Failure).

## STAGE 1 Data Preparation
**1. Load the dataset. How many rows and columns does it have? Print summary statistics for the numeric fields.**
The raw dataset contains approximately 2002 records and 7 features. Summary statistics reveal extreme positive skewness in both budget and revenue, confirming the presence of heavy outliers typical in entertainment economics.

**2. Check for missing values and zeros in budget and revenue. Why can a budget or revenue of 0 be a problem, and how will you handle these rows?**
Zero values in `budget` or `revenue` are artifacts of missing data, not genuine $0 transactions. Retaining them heavily corrupts the target variable calculation. We must drop these records (listwise deletion). While this reduces sample size and introduces survivorship bias (failed indie movies often lack reported financials), imputing such highly skewed financial metrics without external data is statistically invalid.

**3. Create the target column success = 1 when revenue > budget, else 0. What proportion of movies are successful? Is the dataset balanced?**
Post-cleaning, the dataset exhibits a class imbalance skewed toward "Success". This is a classic case of survivorship bias—films that secure theatrical releases and report revenues are inherently more likely to have recouped costs. The imbalance is acceptable for a baseline but warrants monitoring of precision/recall metrics rather than relying solely on global accuracy.

**4. The genres column often holds multiple genres per movie. How will you process it so it can be used for filtering and analysis?**
The feature is stored as a stringified JSON array. We deserialize it using `ast.literal_eval`, extract the `name` attributes, and apply One-Hot Encoding (OHE) or Multi-Label Binarization to transform categorical text into a sparse numeric matrix suitable for tree-based algorithms.

## STAGE 2 Exploratory Data Analysis
**1. Plot Budget vs. Revenue using a scatter plot. Describe the relationship. Do higher budgets tend to earn higher revenue?**
There is a positive but heteroscedastic correlation between budget and revenue. The variance of revenue expands significantly as the budget increases. While higher budgets correlate with higher revenue ceilings, they also increase the absolute magnitude of potential financial loss. It is not a guaranteed linear return.

**2. Explore genre trends: which genres are most common, and which tend to be most successful? Visualise your answer.**
Drama and Comedy dominate by sheer volume. However, genre is a weak standalone predictor. Mainstream genres like Action/Adventure show high gross potential but require massive capital expenditure. Niche genres like Horror often exhibit the highest ROI due to low baseline production costs.

**3. Examine how popularity, runtime, and vote_average relate to success. Which of these looks most associated with a successful movie?**
`vote_average` (critical/audience reception) and `popularity` are the strongest separators between the two classes. Successful films possess statistically higher medians in these metrics. `runtime` shows marginal to negligible predictive power and could likely be dropped to reduce dimensionality.

**4. Produce a correlation heatmap of the numeric features. Which pairs are strongly correlated, and does that raise any concerns for modelling?**
`budget` and `revenue` exhibit strong collinearity. Crucially, `revenue` must be excluded from the feature space. Including it causes catastrophic data leakage, as `revenue` mathematically determines the target variable `success`. 

## STAGE 3 Statistical Testing
**1. Run a T-Test to check whether a numeric feature (e.g. popularity or vote_average) differs significantly between successful and unsuccessful movies. State your null hypothesis, the p-value, and your conclusion.**
- **H0:** µ_success_vote = µ_fail_vote (No difference in mean vote average).
- **P-value:** < 0.05
- **Conclusion:** H0 is rejected. The difference in means is statistically significant. Audience reception is a valid discriminant feature for profitability.

**2. Run a Chi-Square test to check whether a categorical feature (e.g. genre) is associated with success. State the hypothesis, result, and what it means.**
- **H0:** Genre and Success are independent.
- **P-value:** < 0.05
- **Conclusion:** H0 is rejected. The categorical distribution of success is dependent on genre, justifying its inclusion as a predictive feature.

**3. In plain language, what does a p-value tell you? What threshold did you use to decide significance, and why?**
The p-value quantifies the probability of observing the current data distribution assuming there is no actual underlying effect (the null hypothesis). We utilize the standard alpha threshold of 0.05 (5%). A p-value below this threshold indicates the observed relationship is highly unlikely to be random noise.

## STAGE 4 Predictive Modeling (Random Forest)
**1. Select your features and target. Which columns did you feed the model, and why did you exclude any (e.g. title, or revenue itself)?**
- **Included:** `budget`, `popularity`, `runtime`, `vote_average`, and One-Hot Encoded genre variables.
- **Excluded:** `title` (high-cardinality noise without NLP), `revenue` (data leakage).
- **Target:** `success`.

**2. Split the data into training and test sets. What split ratio did you use, and why is a separate test set important?**
An 80/20 train-test split was implemented. An isolated holdout set is non-negotiable to evaluate out-of-sample generalization. Without it, we cannot detect overfitting—where the model memorizes the training data noise instead of learning the underlying signal.

**3. Train a Random Forest Classifier. Briefly explain, in your own words, how a random forest makes a prediction.**
Random Forest is an ensemble learning method. It constructs a multitude of decision trees during training, injecting randomness via bootstrapping (sampling data with replacement) and feature subsampling. During inference, it aggregates the predictions of all individual trees (via majority voting for classification) to yield a final output. This drastically reduces the variance and overfitting inherent in single decision trees.

**4. Evaluate the model using accuracy, precision, recall, and a confusion matrix. How well does it predict success? Where does it make the most mistakes?**
While global accuracy is acceptable, precision and recall reveal the model's true operational value. The model struggles with False Positives—predicting success for high-budget films that ultimately bombed. It fundamentally relies on the general historical trend that "more money = more success," failing to capture the nuance of poorly executed high-budget films.

**5. Inspect feature importance. Which features matter most for predicting success? Does this agree with your EDA and statistical tests?**
Gini impurity-based feature importance ranks `budget`, `vote_average`, and `popularity` as the primary drivers. This perfectly corroborates the findings from the correlation analysis and inferential testing conducted during EDA.

## STAGE 5 Streamlit Dashboard & Deployment
**1. Build a Streamlit dashboard that lets a user filter by genre and by minimum vote average via the sidebar, and updates the visuals accordingly.**
Implemented as a reactive frontend interface.

**2. Display your key EDA charts and statistical-test results inside the app.**
Integrated via Plotly for interactive data visualization.

**3. Add a section where a user can input a movie's details and receive a success / not-success prediction from your trained model.**
Inference pipeline linked to the serialized (`.pkl`) Random Forest model.

**4. Write a requirements.txt and run the app locally with streamlit run MovieIQ.py. Confirm it launches cleanly.**
Environment dependencies documented and verified.

**5. (Bonus) Deploy the app publicly (e.g. Streamlit Community Cloud) and include the live link. What did you have to change for deployment to work?**
Deployed. Required ensuring all file paths were relative rather than absolute, and environment dependencies were strictly version-pinned.

## Reflection (No Sugarcoating)
The current model architecture is fundamentally flawed for pre-production predictive forecasting. It utilizes `vote_average` and `popularity`—metrics that are exclusively generated *post-release*. In a real-world studio setting, predicting a movie's success using its post-release reception is a circular and useless exercise. 

**Critical Improvements Needed:**
1. **Temporal Data Integrity:** We must restrict features strictly to pre-release data (e.g., director historical ROI, lead actor box office draw, intellectual property/franchise status, marketing budget).
2. **Advanced Metrics:** The definition of success must be overhauled to account for theatrical splits (~50%), P&A costs (often matching production budget), and inflation.
3. **Algorithm:** While Random Forest is a decent baseline, gradient boosting architectures (XGBoost/LightGBM) typically yield superior performance on tabular data and should be evaluated.
