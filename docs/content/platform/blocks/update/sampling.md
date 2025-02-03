
## Data Sampling

### What it is
A versatile data sampling tool that can select specific items from a dataset using various selection methods.

### What it does
Takes a collection of data items and returns a smaller subset based on user-defined criteria and sampling methods. It can work with different types of data collections and offers multiple ways to choose which items to include in the sample.

### How it works
The system looks at your data collection and selects items based on your chosen sampling method. It can pick items:
- Completely randomly
- At regular intervals
- From specific groups proportionally
- Based on importance weights
- In clusters or groups
- From the beginning or end
- Using reservoir sampling for streaming data

### Inputs
- Data: The collection of items you want to sample from
- Sample Size: How many items you want in your final selection
- Sampling Method: How you want to choose the items (random, systematic, top, bottom, stratified, weighted, reservoir, or cluster)
- Accumulate: Whether to collect data over time before sampling
- Random Seed: A number to ensure you get the same results each time (optional)
- Stratify Key: The category to use when ensuring balanced group representation
- Weight Key: The value to use when considering item importance
- Cluster Key: The group identifier for cluster-based sampling

### Outputs
- Sampled Data: The selected items from your dataset
- Sample Indices: The positions of the selected items in the original dataset

### Possible use cases
- Quality control in manufacturing: Randomly selecting products for inspection
- Market research: Selecting a representative group of customers to survey
- Data analysis: Creating balanced training datasets for machine learning
- Scientific research: Selecting specimens for detailed analysis
- Social studies: Choosing participants for a study while maintaining demographic balance
