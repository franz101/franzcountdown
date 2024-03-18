import streamlit as st
import requests
import json
from packaging import version
from datetime import datetime, timedelta

def remove_a_week(date_str):
    original_date = datetime.strptime(date_str, "%Y-%m-%d")
    new_date = original_date - timedelta(days=7)
    return new_date.strftime("%Y-%m-%d")

is_stable = lambda x: not (x.is_devrelease or  x.is_postrelease or x.is_prerelease)

def filter_latest_version(p):
  stable_versions = [x for x in p if is_stable(version.parse(x['name']))]
  sorted_versions = sorted(stable_versions, key=lambda x: version.parse(x['name']), reverse=True)
  latest_version = sorted_versions[0]['name']
  return latest_version

def get_latest_version(name,d=""):
  p = get_metadata(name,d)
  v = filter_latest_version(p)
  return v

def get_metadata(name, end_date=""):
  if end_date == "":
    end_date = datetime.now().strftime("%Y-%m-%d")
  if not isinstance(end_date , str):
    end_date = end_date.strftime("%Y-%m-%d")
  start_date = remove_a_week(end_date)
  r = requests.get(f"https://clickpy.clickhouse.com/dashboard/{name}?_rsc=dnxtz&min_date={start_date}&max_date={end_date}",
    headers={
        "Accept-Encoding": "gzip, deflate",
        "Next-Router-State-Tree": "%5B%22%22%2C%7B%22children%22%3A%5B%22dashboard%22%2C%7B%22children%22%3A%5B%5B%22package_name%22%2C%22vaex%22%2C%22d%22%5D%2C%7B%22children%22%3A%5B%22__PAGE__%3F%7B%5C%22min_date%5C%22%3A%5C%22" +start_date+ "%5C%22%2C%5C%22max_date%5C%22%3A%5C%22" + end_date+"%5C%22%7D%22%2C%7B%7D%5D%7D%5D%7D%5D%7D%2Cnull%2Cnull%2Ctrue%5D",
        "RSC": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15"
    },
    cookies={},
    auth=(),
)
  r = r.text.split('{"type":"pie","data":')[1].split("]")[0] +"]"
  p = json.loads(r)
  return p


st.title("Package Version Lookup")
package_name = st.text_input("Enter the package/s name:", "numpy,pandas")
d = st.date_input("What date?", datetime.now())
st.write('Looking for versions on:', d)


    
if st.button("Get Latest Version"):
    try:
        date_str = d.strftime("%Y-%m-%d")
        scraped_packages = []
        package_names = package_name.split(",")
        for pn in package_names:
            pn = pn.strip()
            try:
                latest_version = get_latest_version(pn,date_str)
                scraped_packages.append(tuple([pn,latest_version]))
                st.success(f"{pn} stable version on {date_str} is {latest_version}")
            except IndexError as e:
                scraped_packages.append(tuple([pn,"not-found"]))
        #if package_names:
        #    st.success(f"{package_name} stable version on {date_str} is {latest_version}")
        if not package_names:
            st.error(f"No stable version found for {package_name}")
    except Exception as e:
        st.error(f"Error retrieving data for {package_name}: {e}")
