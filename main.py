from mcp.server.fastmcp import FastMCP
import os, requests, time

EPO_KEY = os.getenv("EPO_KEY") or os.getenv("EPO_CONSUMER_KEY")
EPO_SECRET = os.getenv("EPO_SECRET") or os.getenv("EPO_CONSUMER_SECRET")
BASE = "https://ops.epo.org/3.2/rest-services"

mcp = FastMCP("EPO-MCP")
_token = None
_token_expire = 0

def get_token():
    global _token, _token_expire
    if _token and time.time() < _token_expire - 30:
        return _token
    resp = requests.post(
        "https://ops.epo.org/3.2/auth/accesstoken",
        data={"grant_type": "client_credentials"},
        auth=(EPO_KEY, EPO_SECRET)
    )
    resp.raise_for_status()
    data = resp.json()
    _token = data["access_token"]
    _token_expire = time.time() + int(data["expires_in"])
    return _token

def ops_get(url, params=None):
    token = get_token()
    r = requests.get(
        url,
        params=params,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        },
        timeout=30
    )
    r.raise_for_status()
    return r.json()

# --- 1. Search published patents (CQL) ---
@mcp.tool()
def search_patents(
    q: str,
    range: str = "1-200"
) -> dict:
    """
    Search published patent data using EPO OPS CQL syntax.

    IMPORTANT: Only EPO OPS CQL fields are accepted! Example fields:
        - pa: applicant (e.g., pa=huawei)
        - ti: title (e.g., ti="wireless")
        - ab: abstract (e.g., ab="CSI-RS")
        - pd: publication date (e.g., pd within "2021")
        - ap: application number (e.g., ap=CN2023123456)
        - all: all fields (e.g., all="5G")
        - ic: IPC classification (e.g., ic="H04L")
        - pn: publication number
        - an: application number
        - and, or, within: logic operators
        - any: for matching specific patent offices (e.g., pn any "US")
        - All CQL logical operators (and, or, within) must be lowercase.
        - If a search using 'all=' fails, retry the same query using only 'ti=' and/or 'ab=' fields.
    Examples:
        q="pa=huawei and pd within \"2021\" and (all=\"CSI-RS\" OR all=\"channel state information reference signal\")"
        q="ti=\"wireless communication\" and pa=qualcomm and pd=2020"
        
        if limited to a national patent office(for example, US):, 
        pa=huawei and pd=2021 and (all="CSI-RS" or all="channel state information reference signal") and pn any "US"

    Args:
        q: CQL query string using EPO OPS fields and syntax only.
        range: Page range, e.g., "1-25" (max 100 per page).

    Returns:
        JSON result with biblio data.
    """

    url = BASE + "/published-data/search"
    params = {"q": q, "Range": range}
    return ops_get(url, params)

# --- 2. Retrieve bibliographic data ---
@mcp.tool()
def get_biblio(
    number: str,
    ref_type: str = "publication",
    ref_format: str = "epodoc"
) -> dict:
    """
    Retrieve bibliographic data for a given patent, publication, or application number.

    Args:
        number: Patent/publication/application number. For example: "EP1000000".
        ref_type: Reference type. Allowed values: "publication", "application".
        ref_format: Number format. Allowed values: "epodoc", "docdb", "original".

    Returns:
        JSON bibliographic data, including inventors, applicants, titles, etc.
    """
    url = f"{BASE}/published-data/{ref_type}/{ref_format}/{number}/biblio"
    return ops_get(url)

# --- 3. Retrieve abstract ---
@mcp.tool()
def get_abstract(
    number: str,
    ref_type: str = "publication",
    ref_format: str = "epodoc"
) -> dict:
    """
    Retrieve abstract text for a given patent, publication, or application number.

    Args:
        number: Patent/publication/application number (e.g., "EP1000000").
        ref_type: Reference type ("publication", "application").
        ref_format: Number format ("epodoc", "docdb", "original").

    Returns:
        JSON abstract text and related metadata.
    """
    url = f"{BASE}/published-data/{ref_type}/{ref_format}/{number}/abstract"
    return ops_get(url)

# --- 4. Retrieve full-cycle data ---
@mcp.tool()
def get_full_cycle(
    number: str,
    ref_type: str = "publication",
    ref_format: str = "epodoc"
) -> dict:
    """
    Retrieve full-cycle data for a patent, publication, or application number.
    This includes citations, search reports, and related documents.

    Args:
        number: Patent/publication/application number (e.g., "EP1000000").
        ref_type: Reference type ("publication", "application").
        ref_format: Number format ("epodoc", "docdb", "original").

    Returns:
        JSON full-cycle data.
    """
    url = f"{BASE}/published-data/{ref_type}/{ref_format}/{number}/full-cycle"
    return ops_get(url)

# --- 5. Retrieve INPADOC family data ---
@mcp.tool()
def get_family(
    number: str,
    ref_type: str = "publication",
    ref_format: str = "epodoc",
    biblio: bool = False,
    legal: bool = False
) -> dict:
    """
    Retrieve INPADOC family information for a patent, publication, or application number.

    Args:
        number: Patent/publication/application number (e.g., "EP1000000").
        ref_type: Reference type ("publication", "application").
        ref_format: Number format ("epodoc", "docdb", "original").
        biblio: If True, retrieve only family bibliographic info.
        legal: If True, retrieve only family legal info.

    Returns:
        JSON family data, including all family members (biblio, legal, or both).
    """
    if biblio:
        url = f"{BASE}/family/{ref_type}/{ref_format}/{number}/biblio"
    elif legal:
        url = f"{BASE}/family/{ref_type}/{ref_format}/{number}/legal"
    else:
        url = f"{BASE}/family/{ref_type}/{ref_format}/{number}"
    return ops_get(url)

# --- 6. Retrieve legal event status ---
@mcp.tool()
def get_legal(
    number: str,
    ref_type: str = "publication",
    ref_format: str = "epodoc"
) -> dict:
    """
    Retrieve legal status/event data for a patent, publication, or application number.

    Args:
        number: Patent/publication/application number (e.g., "EP1000000").
        ref_type: Reference type ("publication", "application").
        ref_format: Number format ("epodoc", "docdb", "original").

    Returns:
        JSON legal status data, including legal events and procedural information.
    """
    url = f"{BASE}/legal/{ref_type}/{ref_format}/{number}"
    return ops_get(url)

# --- 7. Patent number conversion ---
@mcp.tool()
def convert_number(
    number: str,
    ref_type: str = "publication",
    input_format: str = "epodoc",
    output_format: str = "docdb"
) -> dict:
    """
    Convert a patent, publication, or application number between EPO's official number formats.

    Args:
        number: Patent/publication/application number to convert (e.g., "EP1000000").
        ref_type: Reference type ("publication", "application").
        input_format: Input number format ("epodoc", "docdb", "original").
        output_format: Output number format ("epodoc", "docdb", "original").

    Returns:
        JSON result with converted number and formats.
    """
    url = f"{BASE}/number-service/{ref_type}/{input_format}/{number}/{output_format}"
    return ops_get(url)

if __name__ == "__main__":
    mcp.run(transport="stdio")