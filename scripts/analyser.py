import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Load cleaned data
df = pd.read_csv("../data/processed/cleaned_venues.csv")

# Replace 'N/A' with actual missing values for processing
df.replace("N/A", pd.NA, inplace=True)

# Convert price_numeric and rating to numbers
df["price_numeric"] = pd.to_numeric(df["price_numeric"], errors="coerce")
df["rating"] = pd.to_numeric(df["rating"], errors="coerce")

# ==================
# Chart 1: Venues per Location
# ==================
venue_counts = df["location"].value_counts().head(10)

plt.figure(figsize=(10,6))
venue_counts.plot(kind="bar", color="skyblue")
plt.title("Top 10 Locations by Venue Count")
plt.xlabel("Location")
plt.ylabel("Number of Venues")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("../plots/venues_per_location.png")
plt.clf()

# ==================
# Chart 2: Avg Price by Location
# ==================
avg_price = df.groupby("location")["price_numeric"].mean().dropna().sort_values(ascending=False).head(10)

plt.figure(figsize=(10,6))
avg_price.plot(kind="bar", color="orange")
plt.title("Top 10 Locations by Avg Price")
plt.ylabel("Avg Price (£)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("../plots/avg_price_by_location.png")
plt.clf()

# ==================
# Chart 2B: Boxplot of Price by Price Type
# ==================
plt.figure(figsize=(10, 6))
sns.boxplot(data=df, x="price_type", y="price_numeric", palette="Set2")
plt.title("Price Distribution by Price Type")
plt.xlabel("Price Type")
plt.ylabel("Price (£)")
plt.tight_layout()
plt.savefig("../plots/price_by_price_type.png")
plt.clf()

# ==================
# Chart 3: Rating vs Price Scatter
# ==================
plt.figure(figsize=(10,6))
sns.scatterplot(data=df, x="price_numeric", y="rating")
plt.title("Rating vs Price")
plt.xlabel("Price (£)")
plt.ylabel("Rating")
plt.tight_layout()
plt.savefig("../plots/rating_vs_price.png")
plt.clf()

# ==================
# Chart 4: Missing Data Heatmap
# ==================
plt.figure(figsize=(12, 6))
sns.heatmap(df.isna(), cbar=False, cmap="YlOrRd")
plt.title("Missing Data Heatmap")
plt.tight_layout()
plt.savefig("../plots/missing_data_heatmap.png")
plt.clf()

print("✅ All plots saved to /plots/")