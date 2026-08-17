#!/usr/bin/env python3
"""
Global World Archives Issue Generator

This script creates a hierarchical GitHub issue structure for cataloging
libraries, archives, and databases across all continents and countries.

Usage:
    python3 generate-world-issues.py --token YOUR_GITHUB_TOKEN --owner jtmlis --repo major-text-archives-table
"""

import csv
import json
import requests
import argparse
import time
from typing import Dict, List, Set
from collections import defaultdict

# Country to Continent mapping
COUNTRY_TO_CONTINENT = {
    # Africa
    'Algeria': 'Africa', 'Angola': 'Africa', 'Benin': 'Africa', 'Botswana': 'Africa',
    'Burkina Faso': 'Africa', 'Burundi': 'Africa', 'Cameroon': 'Africa', 'Cape Verde': 'Africa',
    'Central African Republic': 'Africa', 'Chad': 'Africa', 'Comoros': 'Africa', 'Democratic Republic of the Congo': 'Africa',
    'Djibouti': 'Africa', 'Egypt': 'Africa', 'Equatorial Guinea': 'Africa', 'Eritrea': 'Africa',
    'Eswatini': 'Africa', 'Ethiopia': 'Africa', 'Gabon': 'Africa', 'The Gambia': 'Africa',
    'Ghana': 'Africa', 'Guinea': 'Africa', 'Guinea-Bissau': 'Africa', 'Ivory Coast': 'Africa',
    'Kenya': 'Africa', 'Lesotho': 'Africa', 'Liberia': 'Africa', 'Libya': 'Africa',
    'Madagascar': 'Africa', 'Malawi': 'Africa', 'Mali': 'Africa', 'Mauritania': 'Africa',
    'Mauritius': 'Africa', 'Morocco': 'Africa', 'Mozambique': 'Africa', 'Namibia': 'Africa',
    'Niger': 'Africa', 'Nigeria': 'Africa', 'Republic of the Congo': 'Africa', 'Rwanda': 'Africa',
    'Senegal': 'Africa', 'Seychelles': 'Africa', 'Sierra Leone': 'Africa', 'Somalia': 'Africa',
    'South Africa': 'Africa', 'South Sudan': 'Africa', 'Sudan': 'Africa', 'Tanzania': 'Africa',
    'Togo': 'Africa', 'Tunisia': 'Africa', 'Uganda': 'Africa', 'Zambia': 'Africa', 'Zimbabwe': 'Africa',
    'Somaliland': 'Africa',
    
    # Asia
    'Afghanistan': 'Asia', 'Armenia': 'Asia', 'Azerbaijan': 'Asia', 'Bahrain': 'Asia',
    'Bangladesh': 'Asia', 'Bhutan': 'Asia', 'People\'s Republic of China': 'Asia', 'Georgia': 'Asia',
    'Hong Kong': 'Asia', 'India': 'Asia', 'Indonesia': 'Asia', 'Iran': 'Asia',
    'Iraq': 'Asia', 'Israel': 'Asia', 'Japan': 'Asia', 'Jordan': 'Asia',
    'Kazakhstan': 'Asia', 'Kuwait': 'Asia', 'Kyrgyzstan': 'Asia', 'Laos': 'Asia',
    'Lebanon': 'Asia', 'Maldives': 'Asia', 'Malaysia': 'Asia', 'Mongolia': 'Asia',
    'Myanmar': 'Asia', 'Nepal': 'Asia', 'North Korea': 'Asia', 'Oman': 'Asia',
    'Pakistan': 'Asia', 'Palestine': 'Asia', 'Philippines': 'Asia', 'Qatar': 'Asia',
    'Saudi Arabia': 'Asia', 'Singapore': 'Asia', 'South Korea': 'Asia', 'Syria': 'Asia',
    'Tajikistan': 'Asia', 'Thailand': 'Asia', 'Timor-Leste': 'Asia', 'Turkey': 'Asia',
    'Turkmenistan': 'Asia', 'United Arab Emirates': 'Asia', 'Uzbekistan': 'Asia', 'Vietnam': 'Asia',
    'Yemen': 'Asia', 'Kingdom of the Netherlands': 'Asia', 'Brunei': 'Asia',
    
    # Europe
    'Albania': 'Europe', 'Andorra': 'Europe', 'Austria': 'Europe', 'Belarus': 'Europe',
    'Belgium': 'Europe', 'Bosnia and Herzegovina': 'Europe', 'Bulgaria': 'Europe', 'Croatia': 'Europe',
    'Cyprus': 'Europe', 'Czech Republic': 'Europe', 'Denmark': 'Europe', 'Estonia': 'Europe',
    'Finland': 'Europe', 'France': 'Europe', 'Germany': 'Europe', 'Greece': 'Europe',
    'Greenland': 'Europe', 'Hungary': 'Europe', 'Iceland': 'Europe', 'Ireland': 'Europe',
    'Italy': 'Europe', 'Kosovo': 'Europe', 'Latvia': 'Europe', 'Liechtenstein': 'Europe',
    'Lithuania': 'Europe', 'Luxembourg': 'Europe', 'Malta': 'Europe', 'Moldova': 'Europe',
    'Monaco': 'Europe', 'Montenegro': 'Europe', 'Netherlands': 'Europe', 'North Macedonia': 'Europe',
    'Norway': 'Europe', 'Poland': 'Europe', 'Portugal': 'Europe', 'Romania': 'Europe',
    'Russia': 'Europe', 'San Marino': 'Europe', 'Serbia': 'Europe', 'Slovakia': 'Europe',
    'Slovenia': 'Europe', 'Spain': 'Europe', 'Sweden': 'Europe', 'Switzerland': 'Europe',
    'Ukraine': 'Europe', 'United Kingdom': 'Europe', 'Kingdom of Denmark': 'Europe',
    
    # North America
    'Antigua and Barbuda': 'North America', 'The Bahamas': 'North America', 'Barbados': 'North America',
    'Belize': 'North America', 'Canada': 'North America', 'Costa Rica': 'North America',
    'Cuba': 'North America', 'Dominica': 'North America', 'Dominican Republic': 'North America',
    'El Salvador': 'North America', 'Grenada': 'North America', 'Guatemala': 'North America',
    'Haiti': 'North America', 'Honduras': 'North America', 'Jamaica': 'North America',
    'Mexico': 'North America', 'Nicaragua': 'North America', 'Panama': 'North America',
    'Saint Kitts and Nevis': 'North America', 'Saint Lucia': 'North America',
    'Saint Vincent and the Grenadines': 'North America', 'Trinidad and Tobago': 'North America',
    'United States': 'North America',
    
    # South America
    'Argentina': 'South America', 'Bolivia': 'South America', 'Brazil': 'South America',
    'Chile': 'South America', 'Colombia': 'South America', 'Ecuador': 'South America',
    'Guyana': 'South America', 'Paraguay': 'South America', 'Peru': 'South America',
    'Suriname': 'South America', 'Uruguay': 'South America', 'Venezuela': 'South America',
    
    # Oceania
    'Australia': 'Oceania', 'Fiji': 'Oceania', 'Kiribati': 'Oceania',
    'Marshall Islands': 'Oceania', 'Federated States of Micronesia': 'Oceania',
    'Nauru': 'Oceania', 'New Zealand': 'Oceania', 'Palau': 'Oceania',
    'Papua New Guinea': 'Oceania', 'Samoa': 'Oceania', 'Solomon Islands': 'Oceania',
    'Tonga': 'Oceania', 'Tuvalu': 'Oceania', 'Vanuatu': 'Oceania',
}

CONTINENT_DETAILS = {
    'World': {
        'tag': 'world-archives',
        'emoji': '🌍'
    },
    'Africa': {
        'tag': 'continent-africa',
        'emoji': '🌍',
        'description': 'Cataloging libraries, archives, and databases across the African continent'
    },
    'Asia': {
        'tag': 'continent-asia',
        'emoji': '🌏',
        'description': 'Cataloging libraries, archives, and databases across the Asian continent'
    },
    'Europe': {
        'tag': 'continent-europe',
        'emoji': '🌍',
        'description': 'Cataloging libraries, archives, and databases across the European continent'
    },
    'North America': {
        'tag': 'continent-north-america',
        'emoji': '🌎',
        'description': 'Cataloging libraries, archives, and databases across North America (includes Central America & Caribbean)'
    },
    'South America': {
        'tag': 'continent-south-america',
        'emoji': '🌎',
        'description': 'Cataloging libraries, archives, and databases across South America'
    },
    'Oceania': {
        'tag': 'continent-oceania',
        'emoji': '🌏',
        'description': 'Cataloging libraries, archives, and databases across Oceania and the Pacific'
    },
}

def generate_world_issue_body() -> str:
    """Generate the body for the World issue."""
    return """# Global World Archives Research Initiative

This is the root issue for coordinating a comprehensive catalog of libraries, archives, databases, and knowledge sources across the entire world. The goal is to document and index all available repositories of human knowledge—both digital and physical.

## Mission

To create a complete, globally-comprehensive mapping of text archives, libraries, research databases, and knowledge repositories organized by:
1. **Continents** (7 major regions)
2. **Countries** (193+ sovereign nations)
3. **Administrative divisions** (states, provinces, regions)
4. **Local resources** (municipal libraries, university collections, private archives)

## Research Focus Areas

For each geographic region, we seek to identify and catalog:

### **National & Regional Collections**
- National libraries and archives
- State/provincial libraries and archives
- Municipal library systems
- Regional research institutes

### **Academic Institutions**
- University libraries
- Research institute collections
- Academic archives and special collections
- University museum collections

### **Specialized Archives & Databases**
- Historical archives and manuscripts
- Legal document repositories
- Medical and scientific archives
- Cultural heritage collections
- Government records repositories

### **Digital Resources & Platforms**
- Digital library platforms (Internet Archive, Europeana, etc.)
- Full-text databases (JSTOR, Project MUSE, CORE, etc.)
- Open access repositories (arXiv, PubMed Central, SSRN, etc.)
- Institutional repositories
- Digitized newspaper archives
- Digital humanities projects

### **Special Collections & Rare Books**
- Rare manuscript libraries
- Historical document collections
- First edition and antiquarian collections
- Local history collections
- Family archives and genealogical resources

### **International & Cross-Border Resources**
- UNESCO Memory of the World registers
- World Bank Open Knowledge Repository
- UN digital libraries
- International research databases
- Cross-national collaborative projects

### **Offline & Physical Resources**
- Regional historical societies
- Private collections and archives
- Museum libraries
- Church and religious archives
- Corporate archives
- Broadcasting archives

## Structure

This issue serves as the parent for 7 continental issues:
- **Africa** — Contains country-level issues for all African nations
- **Asia** — Contains country-level issues for all Asian nations
- **Europe** — Contains country-level issues for all European nations
- **North America** — Contains country-level issues for North American nations (includes Central America & Caribbean)
- **South America** — Contains country-level issues for all South American nations
- **Oceania** — Contains country-level issues for Pacific and Oceanic nations

Each continent issue contains sub-issues for every sovereign nation/country in that region.

## Data Sources & Knowledge Bases to Explore

- **Wikidata** (wikidata.org) — Structured data about institutions, libraries, archives
- **Wikipedia** — Links to national and regional libraries
- **UNESCO** — International Library Networks
- **IFLA** (International Federation of Library Associations) — Global library directories
- **ARCHIVENET** — International archives directory
- **Library of Congress** — Research tools and international links
- **Google Scholar** — Academic publications and institutional repositories
- **Academic journals** — Many list institutional repositories
- **Government websites** — National and regional cultural ministry sites
- **Internet Archive** — Wayback Machine and archival resources
- **OpenGrey** — European grey literature repository

## How to Contribute

For each country issue:
1. Research national-level archives and libraries
2. Document state/provincial collections
3. List university and academic collections
4. Catalog specialized databases and digital resources
5. Include links to official websites, catalogs, and access points
6. Note any subscription/access restrictions
7. Document offline-only resources
8. Include administrative division links where applicable

## Expected Outcomes

A comprehensive, machine-readable database of global text archives and knowledge repositories suitable for:
- Academic research across regions
- Library science studies
- Digital humanities projects
- Cultural heritage documentation
- Open science initiatives
- Cross-cultural knowledge exchange

---

**Status:** Active Research Project  
**Last Updated:** 2026  
**Contributors Welcome:** Please help expand this global knowledge base!
"""

def generate_continent_issue_body(continent: str) -> str:
    """Generate the body for a continent issue."""
    return f"""# {continent} — Comprehensive Library & Archive Search

This is the parent issue for cataloging all libraries, archives, and databases across the {continent} continent.

## Objective

To create a complete inventory of text archives, libraries, databases, and knowledge repositories throughout {continent}. Each sub-issue documents resources for a specific country within this continent.

## Research Scope for This Continent

For each country in {continent}, we document:

### National Resources
- **National Library:** Primary government archive and library
- **National Archives:** Historical government documents and records
- **State/Provincial Collections:** Regional libraries and archives
- **Municipal Libraries:** City-level library systems and local collections

### Academic & Research Institutions
- University libraries and their special collections
- Research institutes and think tanks
- Academic archives and museum libraries
- Research databases and platforms

### Specialized Archives
- Historical manuscripts and primary sources
- Legal document archives
- Medical and scientific archives
- Cultural heritage collections
- News archives and newspaper digitization projects

### Digital & Open Access Resources
- Digital library platforms
- Open access scholarly databases
- Institutional repositories
- Digitized collections
- Full-text document platforms

### Local & Community Archives
- Regional historical societies
- Local heritage organizations
- Private archives and collections
- Religious institution libraries
- Corporate archives

### Offline-Only Resources
- Physical manuscript collections
- Rare book rooms
- Government document centers
- Private libraries
- UNESCO Memory of the World sites

## Countries in {continent}

Each country listed below has its own dedicated issue (sub-issue of this continent issue):

[See linked sub-issues for individual countries]

## Data Collection Standards

For each resource documented:
1. **Name** — Official name of the institution/resource
2. **Type** — Library, Archive, Database, Digital Platform, etc.
3. **Website** — Official URL (if available)
4. **Collections** — Brief description of holdings
5. **Access** — Public, Academic, Restricted, etc.
6. **Format** — Physical, Digital, Hybrid
7. **Geographic Coverage** — Local, Regional, National, International
8. **Specializations** — Unique collections or focus areas

## Search Strategy

To research resources for each country, explore:
- National government cultural ministry websites
- UNESCO directories and databases
- IFLA member organizations
- Library of Congress country studies
- Wikipedia library and archive articles
- Academic institution websites
- International database registries
- Local government websites
- Search engines with location filters

## Status

**Continent:** {continent}  
**Total Countries:** [To be documented]  
**Progress:** In Progress  

---

*Parent Issue:* World — Global Archives Research Initiative  
*Sibling Continents:* Africa, Asia, Europe, North America, South America, Oceania
"""

def generate_country_issue_body(country: str, continent: str, divisions: List[str] = None) -> str:
    """Generate the body for a country issue."""
    
    divisions_section = ""
    if divisions:
        divisions_section = f"""## Administrative Divisions

This country contains the following administrative divisions, which may each have regional libraries and archives:

{''.join(f'- {div}' + '\n' for div in divisions[:20])}{'... and more' if len(divisions) > 20 else ''}

Consider searching for local resources in each of these regions.

"""
    
    return f"""# {country} — Libraries, Archives & Databases

**Continent:** {continent}  
**Country:** {country}

## Research Mission

Identify and catalog all major libraries, archives, databases, and text repositories for {country}. This includes national, regional, local, and digital resources covering all formats and access types.

## Areas to Research

### National Level
- National Library of {country}
- National Archives
- National Museum Library
- Government Library System
- State information centers

### Regional/Provincial Level
- State and provincial libraries
- Regional archives
- District information centers
- Local government libraries

### Academic & Research Level
- University libraries (all universities)
- University special collections and archives
- Research institute libraries
- Think tanks and policy research centers
- Medical and scientific libraries

### Specialized Collections
- Historical manuscript archives
- Newspaper archives and microfilm collections
- Legal document repositories
- Religious and ecclesiastical archives
- Cultural heritage collections
- UNESCO Memory of the World sites

### Digital Resources
- National digital library projects
- University institutional repositories
- Open access scholarly databases
- Digitized historical collections
- Online newspaper databases
- Subject-specific databases

### Community & Special Archives
- Regional historical societies
- Local heritage organizations
- Private archives and collectors
- Municipal and district libraries
- Private universities and institutions
- Corporate archives

### Offline/Physical Collections
- Museum libraries
- Private rare book collections
- Government records centers
- Religious institution libraries
- Specialized archives not yet digitized

{divisions_section}

## Research Checklist

- [ ] National Library website reviewed
- [ ] National Archives documented
- [ ] University libraries cataloged
- [ ] Government ministry library identified
- [ ] Regional/provincial archives located
- [ ] Specialized collections identified
- [ ] Digital platforms discovered
- [ ] UNESCO sites checked
- [ ] International databases linked
- [ ] Access restrictions noted

## Data to Collect

For each resource found, document:

**Basic Information:**
- Official name
- Type (Library/Archive/Database/etc.)
- Founding year (if known)
- Governance (Public/Academic/Private)

**Access Information:**
- Website URL
- Physical address (if applicable)
- Opening hours
- Access restrictions
- Subscription/fee requirements

**Collections:**
- Primary focus areas
- Size (estimated or actual)
- Format types (books, manuscripts, digital, etc.)
- Geographic or subject coverage

**Contact:**
- Main phone number
- Email address
- Reference desk contact

**Special Features:**
- Notable special collections
- Unique holdings
- Digitization projects
- Online catalog access
- Inter-library loan services

## Resources for Research

### General Research Tools
- Google Scholar (scholar.google.com)
- Wikidata (wikidata.org)
- Wikipedia article for {country}
- Internet Archive (archive.org)
- Open Directory Project

### Library-Specific Directories
- IFLA Library Directory (library.ifla.org)
- World Library and Information Congress proceedings
- Library of Congress country studies
- ALA International Library Connections

### Government Resources
- Official {country} government websites
- National cultural ministry
- UNESCO country page
- Memory of the World register

### Academic Resources
- University of {country} websites
- Academic accreditation databases
- Research institution registries
- ResearchGate and Academia.edu for institutional profiles

### Archival Resources
- ICA (International Council on Archives) members
- ArchivesHub and similar platforms
- Regional archival associations
- Government records management agencies

### Digital Library Platforms
- Europeana (for European countries)
- World Digital Library
- Digital Libraries Federation
- Digitization project registries

## Notes

Add any relevant notes here about:
- Challenges accessing information
- Regional variations in archive organization
- Language barriers or considerations
- Ongoing digitization projects
- Recent institutional mergers/changes
- Recommended search strategies for this country

---

**Continent:** {continent}  
**Status:** Research in Progress  
**Last Updated:** [Date]  

*Parent Issue:* {continent} — Comprehensive Library & Archive Search
"""

class IssueGenerator:
    """Generate GitHub issues for the world archives project."""
    
    def __init__(self, token: str, owner: str, repo: str):
        self.token = token
        self.owner = owner
        self.repo = repo
        self.base_url = f"https://api.github.com/repos/{owner}/{repo}/issues"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.issue_cache = {}  # Map of {title: issue_number}
        
    def create_issue(self, title: str, body: str, labels: List[str] = None) -> int:
        """Create a single GitHub issue."""
        payload = {
            "title": title,
            "body": body,
            "labels": labels or []
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            issue = response.json()
            issue_number = issue['number']
            self.issue_cache[title] = issue_number
            print(f"✓ Created issue #{issue_number}: {title}")
            time.sleep(0.5)  # Rate limiting
            return issue_number
        except requests.exceptions.RequestException as e:
            print(f"✗ Failed to create issue '{title}': {e}")
            return None
    
    def generate_all_issues(self, countries_file: str, divisions_file: str):
        """Generate all issues for the world."""
        
        # Load country data
        countries = {}
        with open(countries_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['countryLabel']:
                    countries[row['countryLabel']] = row['country']
        
        # Load divisions data
        divisions_by_country = defaultdict(list)
        with open(divisions_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                country = row['countryLabel']
                division = row['entityLabel']
                if country and division:
                    divisions_by_country[country].append(division)
        
        # Create World issue
        print("\n[1/3] Creating World issue...")
        world_body = generate_world_issue_body()
        world_issue = self.create_issue(
            "🌍 World — Global Archives Research Initiative",
            world_body,
            labels=["world-archives", "research", "global"]
        )
        
        if not world_issue:
            print("Failed to create world issue. Aborting.")
            return
        
        # Create continent issues
        print("\n[2/3] Creating continent issues...")
        continent_issues = {}
        for continent in ['Africa', 'Asia', 'Europe', 'North America', 'South America', 'Oceania']:
            continent_body = generate_continent_issue_body(continent)
            emoji = CONTINENT_DETAILS[continent]['emoji']
            tag = CONTINENT_DETAILS[continent]['tag']
            
            issue = self.create_issue(
                f"{emoji} {continent} — country library / archive / database searches",
                continent_body,
                labels=[tag, "continent", "research"]
            )
            if issue:
                continent_issues[continent] = issue
        
        # Create country issues
        print("\n[3/3] Creating country issues...")
        country_issues = {}
        total_countries = len(countries)
        for idx, (country_name, country_uri) in enumerate(countries.items(), 1):
            continent = COUNTRY_TO_CONTINENT.get(country_name, 'Unknown')
            if continent == 'Unknown':
                print(f"⚠ Skipping {country_name}: continent not mapped")
                continue
            
            divisions = divisions_by_country.get(country_name, [])
            body = generate_country_issue_body(country_name, continent, divisions)
            
            labels = [
                "country",
                "research",
                f"continent-{continent.lower().replace(' ', '-')}"
            ]
            
            issue = self.create_issue(
                f"📍 {country_name}",
                body,
                labels=labels
            )
            
            if issue:
                country_issues[country_name] = issue
                print(f"  [{idx}/{total_countries}] {country_name} → {continent}")
            
            # Small delay every 10 issues to be respectful to GitHub API
            if idx % 10 == 0:
                time.sleep(2)
        
        # Summary
        print("\n" + "="*60)
        print("ISSUE GENERATION COMPLETE")
        print("="*60)
        print(f"✓ World issue: #{world_issue}")
        print(f"✓ Continent issues: {len(continent_issues)}")
        print(f"✓ Country issues: {len(country_issues)}")
        print(f"✓ Total issues created: {1 + len(continent_issues) + len(country_issues)}")
        print("\nNote: Issues have been created but sub-issue relationships may need")
        print("to be configured manually via GitHub's UI or via additional API calls")
        print("to update issue bodies with cross-references.")

def main():
    parser = argparse.ArgumentParser(description='Generate global world archives issues')
    parser.add_argument('--token', required=True, help='GitHub API token')
    parser.add_argument('--owner', required=True, help='Repository owner')
    parser.add_argument('--repo', required=True, help='Repository name')
    parser.add_argument('--countries', default='data/countries.csv', help='Countries CSV file')
    parser.add_argument('--divisions', default='data/list-of-countries-and-their-administrative-divisions.csv', help='Divisions CSV file')
    
    args = parser.parse_args()
    
    generator = IssueGenerator(args.token, args.owner, args.repo)
    generator.generate_all_issues(args.countries, args.divisions)

if __name__ == '__main__':
    main()