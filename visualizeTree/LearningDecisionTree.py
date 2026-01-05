import pandas as pd     #reading and processing like pandas but faster
import numpy as np
import re, pickle
from urllib.parse import urlparse

class Tree:
  def __init__(self, attribute : str = None): # type: ignore
    self.attribute = str(attribute)           # make sure it's str
    self.children : dict[str, Tree] = {}
    self.label : str = None # type: ignore
    self.isLeaf = False

  def addChild(self, attribute_value : str, subtree: "Tree"):
    self.children[attribute_value] = subtree

  def setLeaf(self, label: str):
    self.isLeaf = True
    self.label = str(label)  # make sure it's str

  def __str__(self) -> str:
    if self.isLeaf:
      return "Leaf: " + self.label

    _str = "Node: " + self.attribute + "\n"
    for value, key in self.children.items():
      _str += "  If " + self.attribute + " == " + str(value) + ":\n"
      subtree_str = str(key).replace("\n", "\n\t")
      _str += "\t" + subtree_str + "\n"
    return _str
  
  def to_dict(self):
    if self.isLeaf:
      return {"name": f"Leaf: {self.label}", "type": "leaf"}
    else:
      return {
        "name": f"Node: {self.attribute}",
        "type": "node",
        "children": [
          {"name": f"{value}", "children": [child.to_dict()]} for value, child in self.children.items()
        ]
      }

def Entropy(dataset) -> float:
  # to numpy because np.unique required numpy
  lastColumn = dataset.iloc[:, -1].to_numpy()

  # Get counts of unique values
  counts : np.ndarray = np.unique(lastColumn, return_counts=True)[1]

  #           DEBUG
  # uniques, counts = np.unique(lastColumn, return_counts=True)
  # print(uniques)
  # print(counts)

  probabilities : np.ndarray = counts / len(lastColumn)

  #           DEBUG
  # print("probabilities" + str(probabilities))

  # Calculate entropy
  entropy = np.sum(-probabilities * np.log2(probabilities))

  return entropy

#aka reminder
def EntropyAttribute(A : str, dataset: pd.DataFrame) -> float:
  # Extract the column A from the dataset
  columnA = dataset[A].to_numpy()

  uniques, counts = np.unique(columnA, return_counts=True)
  total_samples = np.sum(counts)

  info_A = 0.0

  for unique, count in zip(uniques, counts):
    Dj = dataset[dataset[A] == unique]
    info_A += (count / total_samples) * Entropy(Dj)

  return info_A

def Gain(A : str, dataset: pd.DataFrame = None, entropy: float = None) -> float: # type: ignore
  print( "Calculating Gain for attribute: " + A )
  info_A = EntropyAttribute(A, dataset)

  return entropy - info_A

def buildTree(dataset: pd.DataFrame) -> Tree:
    entropy = Entropy(dataset)
    attributes = dataset.columns[:-1].tolist()  # Exclude the label column
    labels = dataset[dataset.columns[-1]]
    uniqueLabels = labels.unique()

    # only one label, make leaf
    if len(uniqueLabels) == 1:
        leaf = Tree()
        leaf.setLeaf(label=uniqueLabels[0])
        return leaf

    # no more attributes to split on, make leaf with most common label
    if len(attributes) == 0:
        leaf = Tree()
        leaf.setLeaf(label=labels.mode()[0]) #mode returns most common and [0] to get value because sometime it having many highest count
        return leaf

    # choose best attribute to split on
    best_attribute : str = max(attributes, key=lambda attr: Gain(attr, dataset, entropy))
    tree = Tree(attribute=best_attribute)
    attributeUniques : np.ndarray = dataset[best_attribute].unique()

    for value in attributeUniques:
        subDataset = dataset[dataset[best_attribute] == value].drop(columns=[best_attribute])
        subTree = buildTree(subDataset)
        tree.addChild(value, subTree)
    return tree

def predict(dataset : pd.DataFrame, tree : Tree) -> list[str]:
    ls = []
    for i in range(len(dataset.index)):
        row = dataset.iloc[i]
        currentNode = tree

        while not currentNode.isLeaf:
            attributeValue = row[currentNode.attribute]

            if attributeValue in currentNode.children:
                currentNode = currentNode.children[attributeValue] #this is dictionary so no question
                continue

            print(f"ERROR: Attribute value {attributeValue} not found in tree children.")
            break

        ls.append(currentNode.label)
    return ls

def getChildrenLabels(tree: Tree) -> set[str]:
    labels = set()
    if tree.isLeaf:
        labels.add(tree.label)
        return labels
    
    for child in tree.children.values():
            labels.update(getChildrenLabels(child))
    return labels

def canPrune(tree: Tree) -> tuple[bool, str]:
    if tree.isLeaf:
        return False, None
    
    labels = getChildrenLabels(tree)
    
    #only 1 label then able to prune
    if len(labels) == 1:
        return True, list(labels)[0]
    
    return False, None

def pruneTree(tree: Tree) -> Tree:
    if tree.isLeaf:
        newTree = Tree()
        newTree.setLeaf(tree.label)
        return newTree
    
    newTree = Tree(tree.attribute)
    
    for value, child in tree.children.items():
        pruned = pruneTree(child)
        newTree.addChild(value, pruned)
    
    canCollapse, label = canPrune(newTree)
    if canCollapse:
        collapsed = Tree()
        collapsed.setLeaf(label)
        return collapsed
    
    return newTree

def calculate_accuracy(predLabels, trueLabels):
    _str = ""
    _len = len(trueLabels)
    totalCorrect = 0
    totalNone = 0
    for i in range(_len):
        trueLabels[i] = str(trueLabels[i])

        _bool = predLabels[i] == trueLabels[i]

        _str += f'Predicted: {predLabels[i]}, True: {trueLabels[i]} -> {_bool}\n'

        if _bool:
            totalCorrect += 1

        if predLabels[i] is None:
            totalNone += 1

    print(_str)
    accuracy = totalCorrect / (_len - totalNone)
    print(f'Accuracy: {totalCorrect} / {_len - totalNone} = {accuracy * 100:.2f}%')

def analyze_mail(email: str) -> pd.DataFrame:
    #[s]? is optional s,
    #(?:...) is non-capturing group
    # ()+ means one or more
    urlMatch = re.search(r'http[s]?://(?:[a-zA-Z0-9$-_@.&+!*\\(\\),#])+', email)
    url = urlMatch.group(0) if urlMatch else ""
    # {2,} means at least 2 char
    # sender_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', email)
    # sender_email = sender_match.group(0) if sender_match else ""

    listSensitiveWords = ['verify', 'account', 'login', 'secure', 'password', 'confirm',
                            'update', 'urgent', 'action', 'required', 'click', 'immediately',
                            'suspended', 'restricted', 'limited']
    listBrandNames = ['paypal', 'apple', 'google', 'amazon', 'microsoft', 'facebook',
                        'netflix', 'ebay']

    parsed = urlparse(url) #bult-in module to parse url
    hostname = parsed.hostname if parsed.hostname else ""
    path = parsed.path if parsed.path else ""

    # subdomains: example: paypal.security-login.example.com -> paypal.security-login
    subdomains = hostname.split('.')[:-2] if len(hostname.split('.')) > 2 else []
    subdomains = '.'.join(subdomains).lower()
    #any() returns true if any of the element is true
    # DomainInSubdomains: count if a known brand name appears in the subdomain part
    domainInSubdomains = any(brand in subdomains for brand in listBrandNames)

    # DomainInPaths: count if a known brand name appears in the path
    domainInPaths = any(brand in path.lower() for brand in listBrandNames)

    # HttpsInHostname: count if 'https' appears in the hostname (not the scheme)
    HttpsInHostname = 'https' in hostname.lower()

    phishingFeatures = {
        'NumDots': url.count('.'),
        'SubdomainLevel': url.count('.') - 1,
        'PathLevel': url.count('/') - 2,
        'UrlLength': len(url),
        'NumDash': url.count('-'),
        'NumDashInHostname': hostname.count('-'),
        'AtSymbol': url.count('@'),
        'TildeSymbol': url.count('~'),
        'NumUnderscore': url.count('_'),
        'NumPercent': url.count('%'),
        'NumQueryComponents': url.count('&') + 1 if '?' in url else 0,
        'NumAmpersand': url.count('&'),
        'NumHash': url.count('#'),
        'NumNumericChars': sum(c.isdigit() for c in url),
        'NoHttps': url.count('https://') == 0,
        'RandomString': 1 if re.search(r'[a-zA-Z0-9]{8,}', url) else 0,
        'IpAddress': 1 if re.match(r'http[s]?://\d+\.\d+\.\d+\.\d+', url) else 0,
        'DomainInSubdomains': int(domainInSubdomains),
        'DomainInPaths': int(domainInPaths),
        'HttpsInHostname': int(HttpsInHostname),
        'HostnameLength': len(hostname),
        'PathLength': len(path),
        'QueryLength': len(parsed.query),
        'DoubleSlashInPath': url.count('//') - 1,
        'NumSensitiveWords': sum(1 for word in listSensitiveWords if word.lower() in email.lower()),
        'EmbeddedBrandName': sum(1 for brand in listBrandNames if brand in email.lower()),
    }

    return divideThresholds(pd.DataFrame([phishingFeatures]))

def storeThresholds(dataset, max_divisions) -> dict:
    thresholds = {}
    for col in dataset.columns:
        if dataset[col].dtype not in [np.int64, np.float64]:
            continue

        max_val = dataset[col].max()
        divideBy = int(max_val / max_divisions)
        
        divideRange = 0
        if divideBy > 1:
            divideRange = int(max_val / divideBy)

        thresholds[col] = {
            'max': max_val,
            'divideBy': divideBy,
            'divideRange': divideRange
        }
    return thresholds

thresholds = None

def divideThresholds(dataset) -> pd.DataFrame:
    for col in dataset.columns:
        if col == dataset.columns[-1]:
            continue
        
        if dataset[col].dtype not in [np.int64, np.float64]:
            continue
       
        if col not in thresholds:
            raise ValueError(f"Column {col} not found in thresholds.")
        
        if thresholds is None:
            raise ValueError("Thresholds have not been initialized.")

        max = thresholds[col]['max']
        divideBy = thresholds[col]['divideBy']
        divideRange = thresholds[col]['divideRange']
        print(f'Dividing column {col} into {divideRange} ranges of {divideBy} each.')

        #convert to string to avoid issues with replacing numeric values with strings
        result_col = dataset[col].astype(str)

        if(divideRange == 0):
            mask = dataset[col] >= max
            result_col[mask] = f'>{max}'
            dataset[col] = result_col
            dataset[col] = dataset[col].astype(str)
            continue

        for i in range(1, divideRange + 1):
            max = divideBy * i
            min = divideBy * (i - 1)
            replaceValue = f'{min} - {max}'
            
            mask = (dataset[col] <= max) & (dataset[col] >= min)
            result_col[mask] = replaceValue

            if i == divideRange:
                mask = dataset[col] > max
                result_col[mask] = f'>{max}'

        # Replace the original numeric column with our new string results
        dataset[col] = result_col

    return dataset

# train_dataset = pd.read_csv("email_phishing_data.csv")
# cols_to_drop = [
#     'PctExtHyperlinks', 'PctExtResourceUrls', 'ExtFavicon', 'InsecureForms',
#     'RelativeFormAction', 'ExtFormAction', 'AbnormalFormAction',
#     'PctNullSelfRedirectHyperlinks', 'FrequentDomainNameMismatch',
#     'FakeLinkInStatusBar', 'RightClickDisabled', 'PopUpWindow',
#     'SubmitInfoToEmail', 'IframeOrFrame', 'MissingTitle',
#     'ImagesOnlyInForm', 'PctExtResourceUrlsRT', 'AbnormalExtFormActionR',
#     'ExtMetaScriptLinkRT', 'PctExtNullSelfRedirectHyperlinksRT',
#     'SubdomainLevelRT', 'UrlLengthRT', #they are null
#     'id'
# ]
# train_dataset.drop(columns=cols_to_drop, inplace=True)

# thresholds = storeThresholds(train_dataset, 10)
# train_dataset = divideThresholds(train_dataset)

# train_dataset = train_dataset.sample(frac=1).reset_index(drop=True) #shuffle

# decision_tree : Tree = buildTree(train_dataset.copy())

# with open('decision_tree.pkl', 'wb') as f:
#     pickle.dump(decision_tree, f)

# with open('thresholds.pkl', 'wb') as f:
#     pickle.dump(thresholds, f)
  
def load_tree(tree_path: str = "decision_tree.pkl", thresholds_path: str = "thresholds.pkl") -> Tree:
    try:
        with open(tree_path, 'rb') as f:
            loaded_tree : Tree = pickle.load(f)
        with open(thresholds_path, 'rb') as f:
            global thresholds
            thresholds = pickle.load(f)
    except FileNotFoundError:
      raise FileExistsError('File not found: ' + tree_path)
    except Exception as e:
      raise RuntimeError(f'{str(e)}\nSuggest to retrain the model to generate the decision_tree.pkl file.')
    return loaded_tree

tree = pruneTree(load_tree())