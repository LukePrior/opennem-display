"""
HyperPixel 2.1 Round OpenNEM Display
"""

# Dependencies
import argparse
import math
import urllib.request
import json
from datetime import date, datetime
import pygame
import numpy as np

# Constants
current_year = date.today().year
previous_year = current_year - 1

last_refresh = datetime.now()
refresh_duration = 5

base_url = "https://data.opennem.org.au/v3/stats/au"

region = "NEM"
period = "week"
version = "default"

network_regions = {
    "NEM": {"url": "/NEM"},
    "NSW": {"url": "/NEM/NSW1"},
    "QLD": {"url": "/NEM/QLD1"},
    "SA": {"url": "/NEM/SA1"},
    "TAS": {"url": "/NEM/TAS1"},
    "VIC": {"url": "/NEM/VIC1"},
    "WA": {"url": "/WEM"}
}

region_list = ["NEM", "NSW", "QLD", "SA", "TAS", "VIC", "WA"]

network_times = {
    "instant": {"display": "Instantaneous", "url": "/power/7d.json", "unit": "MW"},
    "day": {"display": "Yesterday", "url": "/energy/" + str(current_year) + ".json", "unit": "GWh"},
    "week": {"display": "This Week", "url": "/energy/" + str(current_year) + ".json", "unit": "GWh"},
    "month": {"display": "This Month", "url": "/energy/" + str(current_year) + ".json", "unit": "GWh"},
    "year": {"display": "This Year", "url": "/energy/" + str(previous_year) + ".json", "unit": "GWh"}
}

times_list = ["instant", "day", "week", "month", "year"]

graph_types = {
    "default": {"display": "Default"},
    "simplified": {"display": "Simplified"},
    "flexible": {"display": "Flexible"},
    "renewable": {"display": "Renewable"}
}

types_list = ["default", "simplified", "flexible", "renewable"]

technology_simplified = {
    "gas_ocgt": "gas",
    "gas_ccgt": "gas",
    "gas_recip": "gas",
    "gas_steam": "gas",
    "gas_wcmg": "gas",
    "coal_black": "coal",
    "coal_brown": "coal",
    "solar_rooftop": "solar",
    "solar_utility": "solar",
    "wind": "wind",
    "hydro": "hydro",
    "battery": "battery",
    "battery_discharging": "battery_discharging",
    "imports": "import",
    "distillate": "distillate",
    "bioenergy": "bioenergy",
    "bioenergy_biomass": "bioenergy",
    "bioenergy_biogas": "bioenergy"
}

technology_flexible = {
    "gas_ocgt": "fast",
    "gas_ccgt": "fast",
    "gas_recip": "fast",
    "gas_steam": "slow",
    "gas_wcmg": "fast",
    "coal_black": "slow",
    "coal_brown": "slow",
    "solar_rooftop": "variable",
    "solar_utility": "variable",
    "wind": "variable",
    "hydro": "fast",
    "battery": "battery",
    "battery_discharging": "fast",
    "imports": "import",
    "distillate": "fast",
    "bioenergy": "fast",
    "bioenergy_biomass": "fast",
    "bioenergy_biogas": "fast"
}

technology_renewable = {
    "gas_ocgt": "fossil",
    "gas_ccgt": "fossil",
    "gas_recip": "fossil",
    "gas_steam": "fossil",
    "gas_wcmg": "fossil",
    "coal_black": "fossil",
    "coal_brown": "fossil",
    "solar_rooftop": "renewable",
    "solar_utility": "renewable",
    "wind": "renewable",
    "hydro": "renewable",
    "battery": "battery",
    "battery_discharging": "battery_discharging",
    "imports": "import",
    "distillate": "fossil",
    "bioenergy": "renewable",
    "bioenergy_biomass": "renewable",
    "bioenergy_biogas": "renewable"
}

technology_colour = {
    "gas_ocgt": [255, 205, 150],
    "gas_ccgt": [253, 180, 98],
    "gas_recip": [249, 220, 188],
    "gas_steam": [244, 142, 27],
    "gas_wcmg": [180, 104, 19],
    "coal_black": [18, 18, 18],
    "coal_brown": [139, 87, 42],
    "solar_rooftop": [255, 224, 61],
    "solar_utility": [254, 213, 0],
    "imports": [68, 20, 111],
    "import": [68, 20, 110],
    "bioenergy_biomass": [29, 122, 122],
    "bioenergy_biogas": [29, 122, 121],
    "gas": [255, 136, 19],
    "coal": [19, 19, 19],
    "solar": [254, 214, 0],
    "wind": [65, 117, 5],
    "hydro": [69, 130, 180],
    "battery_discharging": [0, 162, 250],
    "battery": [0, 162, 251],
    "distillate": [243, 80, 32],
    "bioenergy": [163, 136, 111],
    "fast": [93, 105, 177],
    "slow": [229, 134, 6],
    "variable": [2, 188, 163],
    "renewable": [82, 188, 163],
    "fossil": [68, 68, 68]
}

technology_order = [
    "variable",
    "fast",
    "slow",
    "renewable",
    "fossil",
    "solar_rooftop",
    "solar_utility",
    "solar",
    "wind",
    "hydro",
    "battery_discharging",
    "battery",
    "gas",
    "gas_wcmg",
    "gas_recip",
    "gas_ocgt",
    "gas_ccgt",
    "gas_steam",
    "distillate",
    "bioenergy",
    "bioenergy_biomass",
    "bioenergy_biogas",
    "coal",
    "coal_black",
    "coal_brown",
    "imports",
    "import"
]

# Combine yearly data
def combine_data(data1, data2):
    for technology in data1["data"]:
        if technology["data_type"] == "energy":
            for technology2 in data2["data"]:
                if technology2["data_type"] == "energy":
                    if technology["code"] == technology2["code"]:
                        technology2["history"]["data"] = technology["history"]["data"] + technology2["history"]["data"]

    return data2
    

# Download data
def download_data(region="NEM", time="month"):   
    url = base_url + network_regions[region]["url"] + network_times[time]["url"]
    response = urllib.request.urlopen(url)
    data = json.loads(response.read())

    if time == "year":
        url2 = base_url + network_regions[region]["url"] + network_times["month"]["url"]
        response2 = urllib.request.urlopen(url2)
        data2 = json.loads(response2.read())
        data = combine_data(data, data2)
    
    return data

# Process data
def process_data(data, time="month"):
    raw = {"default": {}, "simplified": {}, "flexible": {}, "renewable": {}}
    for technology in data["data"]:
        if technology["code"] != "battery_charging" and technology["code"] != "exports" and technology["code"] != "pumps":
            
            amount = 0
            
            if technology["data_type"] == "power": # MW
                if technology["history"]["interval"] == "5m":
                    amount = abs(round(sum(technology["history"]["data"][-6:])/6,1))
                else:
                    amount = abs(round(technology["history"]["data"][-1],1))
                    
            elif technology["data_type"] == "energy": # GWh
                if time == "year":
                    amount = round(sum(technology["history"]["data"][-365:]),1)
                if time == "month":
                    amount = round(sum(technology["history"]["data"][-30:]),1)
                if time == "week":
                    amount = round(sum(technology["history"]["data"][-7:]),1)
                if time == "day":
                    amount = round(sum(technology["history"]["data"][-1:]),1)
                    
            if amount != 0:
                raw["default"][technology["code"]] = amount
                if technology_simplified[technology["code"]] in raw["simplified"]:
                    raw["simplified"][technology_simplified[technology["code"]]] += amount
                    raw["simplified"][technology_simplified[technology["code"]]] = round(raw["simplified"][technology_simplified[technology["code"]]], 1)
                else:
                    raw["simplified"][technology_simplified[technology["code"]]] = amount
                if technology_renewable[technology["code"]] in raw["renewable"]:
                    raw["renewable"][technology_renewable[technology["code"]]] += amount
                    raw["renewable"][technology_renewable[technology["code"]]] = round(raw["renewable"][technology_renewable[technology["code"]]], 1)
                else:
                    raw["renewable"][technology_renewable[technology["code"]]] = amount
                if technology_flexible[technology["code"]] in raw["flexible"]:
                    raw["flexible"][technology_flexible[technology["code"]]] += amount
                    raw["flexible"][technology_flexible[technology["code"]]] = round(raw["flexible"][technology_flexible[technology["code"]]], 1)
                else:
                    raw["flexible"][technology_flexible[technology["code"]]] = amount
                    
    return raw

# Calculate total energy
def calculate_energy(data):
    energy = 0
    for technology in data:
        energy += data[technology]
    energy = round(energy)
    return energy

# Format data
def format_data(raw):
    data = {}
    for technology in raw:
        value = round(raw[technology]/totalpower*360,1)
        if value > 0:
            try:
                data[technology] += value
            except:
                data[technology] = value
    return data         

# Order processed data
def order_data(data):
    ordered_data = {}
    for item in technology_order:
        if item in data:
            ordered_data[item] = data[item]
    return ordered_data

# Get new data given parameters
def refresh_data(region1, period1, version1):
    global data, raw, totalpower, region, period, version
    region = region1
    period = period1
    version = version1
    
    data = download_data(region, period)
    raw = process_data(data, period)
    raw = raw[version]

    totalpower = calculate_energy(raw)

    data = format_data(raw)

    data = order_data(data)

# Read arguments
parser = argparse.ArgumentParser(description='Process region, period, display, and time options.')

parser.add_argument("-r", "--region", type=str, help="Set region ('NEM', 'NSW', 'QLD', 'SA', 'TAS', 'VIC', 'WA')")
parser.add_argument("-p", "--period", type=str, help="Set period ('instant', 'day', 'week', 'month', 'year')")
parser.add_argument("-d", "--display", type=str, help="Set display ('default', 'simplified', 'flexible', 'renewable')")
parser.add_argument("-t", "--time", type=int, help="Set refresh time in minutes")

args = parser.parse_args()

if args.region != None and args.region in region_list:
    region = args.region
if args.period != None and args.period in times_list:
    period = args.period
if args.display != None and args.display in types_list:
    version = args.display
if args.time != None:
    refresh_duration = args.time

# Get data
refresh_data(region, period, version)

# Initialise PyGame
pygame.init()
pygame.font.init()
font = pygame.font.SysFont('Helvetica', 25, bold=True)
screen = pygame.display.set_mode((480, 480), pygame.FULLSCREEN)
#screen = pygame.display.set_mode((480, 480))

# Donut chart properties
white = (255,255,255)
innerCircleX = 240
innerCircleY = 240
innerCircleRadius = 100

active = True

# Navigation variables
hovering = False
hoveringColor = white
hoveringTechnology = ""
hoveringPercentage = ""
hoveringPosition = [0,0]
hoveringTime = datetime.now()
hovering_period = 5
hoveringCount = 0

# Render chart
while active:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
             active = False
        if (event.type == pygame.MOUSEMOTION):
            position = list(pygame.mouse.get_pos())
            distance = ((((position[0] - hoveringPosition[0])**2) + ((position[1] - hoveringPosition[1])**2) )**0.5)
            hoveringPosition = position
            hovering_difference = datetime.now() - hoveringTime
            if hovering_difference.total_seconds() > hovering_period:
                hoveringCount = 1
                hoveringTime = datetime.now()
            elif distance < 60 and hovering_difference.total_seconds() < hovering_period:
                hoveringCount += 1
            else:
                hoveringCount = 0
                hoveringTime = datetime.now()
            if hoveringCount >= 3: # change data
                if position[0] >= 170 and position[0] <= 310 and position[1] >= 170 and position[1] <= 310: # middle
                    index = types_list.index(version)
                    if index > 0:
                        refresh_data(region, period, types_list[index-1])
                    else:
                        refresh_data(region, period, types_list[len(types_list)-1])
                elif position[0] <= 70: # left
                    index = region_list.index(region)
                    if index > 0:
                        refresh_data(region_list[index-1], period, version)
                    else:
                        refresh_data(region_list[len(region_list)-1], period, version)
                elif position[0] >= 410: # right
                    index = region_list.index(region)
                    if index < len(region_list)-1:
                        refresh_data(region_list[index+1], period, version)
                    else:
                        refresh_data(region_list[0], period, version)
                elif position[1] <= 70: # up
                    index = times_list.index(period)
                    if index < len(times_list)-1:
                        refresh_data(region, times_list[index+1], version)
                    else:
                        refresh_data(region, times_list[0], version)
                elif position[1] >= 410: # down
                    index = times_list.index(period)
                    if index > 0:
                        refresh_data(region, times_list[index-1], version)
                    else:
                        refresh_data(region, times_list[len(times_list)-1], version)
                hoveringCount = 0
                hovering = False
            else: # select technology
                color = list(screen.get_at(pygame.mouse.get_pos())[:3])
                values = list(technology_colour.values())
                if color in values:
                    technology = list(technology_colour.keys())[values.index(color)]
                    if (color != hoveringColor or hovering is False) and technology in data:
                        hoveringColor = color
                        hoveringTechnology = technology
                        hoveringPercentage = str(round(data[technology]/3.6,1))+"%"
                        hovering = True
                    else:
                        hovering = False

    # Update periodically
    time_difference = datetime.now() - last_refresh
    if time_difference.total_seconds() > 60 * refresh_duration:
        refresh_data(region, period, version)
        last_refresh = datetime.now()
        hovering = False


    lower = -90
    upper = -90

    screen.fill(white)

    textsurface = font.render(region + " " + str(round(totalpower)) + " " + network_times[period]["unit"], False, (0, 0, 0))
    textsurface2 = font.render(graph_types[version]["display"], False, (0, 0, 0))
    textsurface3 = font.render(network_times[period]["display"], False, (0, 0, 0))
    text_rect = textsurface.get_rect(center=(240, 240))
    text_rect2 = textsurface2.get_rect(center=(240, 210))
    text_rect3 = textsurface3.get_rect(center=(240, 270))

    for technology in data:
        stat = data[technology]
        
        upper += stat

        p = [(240, 240)]

        # Get points on arc
        points = np.linspace(lower,upper,1000)
        for n in points:
            x = 240 + int(250*math.cos(n*math.pi/180))
            y = 240 + int(250*math.sin(n*math.pi/180))
            p.append((x, y))
        p.append((240, 240))

        if len(p) > 2:
            pygame.draw.polygon(screen, technology_colour[technology], p)

        lower += stat

    pygame.draw.circle(screen,white,(innerCircleX,innerCircleY),innerCircleRadius)

    screen.blit(textsurface,text_rect)
    screen.blit(textsurface2,text_rect2)
    screen.blit(textsurface3,text_rect3)
    
    if hovering:
        pygame.draw.circle(screen,white,(innerCircleX,innerCircleY),innerCircleRadius)
        pygame.draw.circle(screen,hoveringColor,(innerCircleX,innerCircleY),innerCircleRadius-5)
        textsurface4 = font.render(hoveringTechnology, False, (255, 255, 255))
        textsurface5 = font.render(hoveringPercentage, False, (255, 255, 255))
        text_rect4 = textsurface4.get_rect(center=(240, 225))
        text_rect5 = textsurface5.get_rect(center=(240, 255))
        screen.blit(textsurface4,text_rect4)
        screen.blit(textsurface5,text_rect5)

    pygame.display.update()
