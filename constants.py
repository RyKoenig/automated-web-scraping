PARENT_DIR = '/home/rkoenig/Web-Scraping-Automation/'

path_to_chromedriver = '/usr/local/bin/chromedriver'

nfl_pfr_team_map = {'Los Angeles Chargers': '1f6dcffb-9823-43cd-9ff4-e7a8466749b5',
                    'New York Giants': '04aa1c9d-66da-489d-b16a-1dee3f2eec4d', 
                    'Arizona Cardinals': 'de760528-1dc0-416a-a978-b510d20692ff', 
                    'Atlanta Falcons': 'e6aa13a4-0055-48a9-bc41-be28dc106929', 
                    'Baltimore Ravens': 'ebd87119-b331-4469-9ea6-d51fe3ce2f1c', 
                    'Buffalo Bills': '768c92aa-75ff-4a43-bcc0-f2798c2e1724', 
                    'Carolina Panthers': 'f14bf5cc-9a82-4a38-bc15-d39f75ed5314', 
                    'Chicago Bears': '7b112545-38e6-483c-a55c-96cf6ee49cb8', 
                    'Cincinnati Bengals': 'ad4ae08f-d808-42d5-a1e6-e9bc4e34d123', 
                    'Cleveland Browns': 'd5a2eb42-8065-4174-ab79-0a6fa820e35e', 
                    'Dallas Cowboys': 'e627eec7-bbae-4fa4-8e73-8e1d6bc5c060', 
                    'Denver Broncos': 'ce92bd47-93d5-4fe9-ada4-0fc681e6caa0', 
                    'Detroit Lions': 'c5a59daa-53a7-4de0-851f-fb12be893e9e', 
                    'Green Bay Packers': 'a20471b4-a8d9-40c7-95ad-90cc30e46932', 
                    'Houston Texans': '82d2d380-3834-4938-835f-aec541e5ece7', 
                    'Indianapolis Colts': '82cf9565-6eb9-4f01-bdbd-5aa0d472fcd9', 
                    'Jacksonville Jaguars': 'f7ddd7fa-0bae-4f90-bc8e-669e4d6cf2de', 
                    'Kansas City Chiefs': '6680d28d-d4d2-49f6-aace-5292d3ec02c2', 
                    'Miami Dolphins': '4809ecb0-abd3-451d-9c4a-92a90b83ca06',
                    'Minnesota Vikings': '33405046-04ee-4058-a950-d606f8c30852', 
                    'New England Patriots': '97354895-8c77-4fd4-a860-32e62ea7382a',
                    'New Orleans Saints': '0d855753-ea21-4953-89f9-0e20aff9eb73', 
                    'New York Jets': '5fee86ae-74ab-4bdd-8416-42a9dd9964f3', 
                    'Philadelphia Eagles': '386bdbf9-9eea-4869-bb9a-274b0bc66e80', 
                    'Los Angeles Rams': '2eff2a03-54d4-46ba-890e-2bc3925548f3', 
                    'Pittsburgh Steelers': 'cb2f9f1f-ac67-424e-9e72-1475cb0ed398', 
                    'Seattle Seahawks': '3d08af9e-c767-4f88-a7dc-b920c6d2b4a8', 
                    'San Francisco 49ers': 'f0e724b0-4cbf-495a-be47-013907608da9', 
                    'Tampa Bay Buccaneers': '4254d319-1bc7-4f81-b4ab-b5e6f3402b69', 
                    'Tennessee Titans': 'd26a1ca5-722d-4274-8f97-c92e49c96315', 
                    'Washington Commanders': '22052ff7-c065-42ee-bc8f-c4691c50e624', 
                    'Las Vegas Raiders': '7d4fcc64-9cb5-4d1b-8e75-8a906d1e1576'}

nba_espn_team_map = {'dallas-mavericks': '583ecf50-fb46-11e1-82cb-f4ce4684ea4c',
                    'golden-state-warriors': '583ec825-fb46-11e1-82cb-f4ce4684ea4c',
                    'utah-jazz': '583ece50-fb46-11e1-82cb-f4ce4684ea4c',
                    'new-orleans-pelicans': '583ecc9a-fb46-11e1-82cb-f4ce4684ea4c',
                    'boston-celtics': '583eccfa-fb46-11e1-82cb-f4ce4684ea4c',
                    'atlanta-hawks': '583ecb8f-fb46-11e1-82cb-f4ce4684ea4c',
                    'toronto-raptors': '583ecda6-fb46-11e1-82cb-f4ce4684ea4c',
                    'memphis-grizzlies': '583eca88-fb46-11e1-82cb-f4ce4684ea4c',
                    'brooklyn-nets': '583ec9d6-fb46-11e1-82cb-f4ce4684ea4c',
                    'indiana-pacers': '583ec7cd-fb46-11e1-82cb-f4ce4684ea4c',
                    'phoenix-suns': '583ecfa8-fb46-11e1-82cb-f4ce4684ea4c',
                    'charlotte-hornets': '583ec97e-fb46-11e1-82cb-f4ce4684ea4c',
                    'oklahoma-city-thunder': '583ecfff-fb46-11e1-82cb-f4ce4684ea4c',
                    'orlando-magic': '583ed157-fb46-11e1-82cb-f4ce4684ea4c',
                    'miami-heat': '583ecea6-fb46-11e1-82cb-f4ce4684ea4c',
                    'new-york-knicks': '583ec70e-fb46-11e1-82cb-f4ce4684ea4c',
                    'philadelphia-76ers': '583ec87d-fb46-11e1-82cb-f4ce4684ea4c',
                    'detroit-pistons': '583ec928-fb46-11e1-82cb-f4ce4684ea4c',
                    'san-antonio-spurs': '583ecd4f-fb46-11e1-82cb-f4ce4684ea4c',
                    'minnesota-timberwolves': '583eca2f-fb46-11e1-82cb-f4ce4684ea4c',
                    'sacramento-kings': '583ed0ac-fb46-11e1-82cb-f4ce4684ea4c',
                    'houston-rockets': '583ecb3a-fb46-11e1-82cb-f4ce4684ea4c',
                    'milwaukee-bucks': '583ecefd-fb46-11e1-82cb-f4ce4684ea4c',
                    'cleveland-cavaliers': '583ec773-fb46-11e1-82cb-f4ce4684ea4c',
                    'washington-wizards': '583ec8d4-fb46-11e1-82cb-f4ce4684ea4c',
                    'los-angeles-clippers': '583ecdfb-fb46-11e1-82cb-f4ce4684ea4c',
                    'portland-trail-blazers': '583ed056-fb46-11e1-82cb-f4ce4684ea4c',
                    'chicago-bulls': '583ec5fd-fb46-11e1-82cb-f4ce4684ea4c',
                    'denver-nuggets': '583ed102-fb46-11e1-82cb-f4ce4684ea4c',
                    'los-angeles-lakers': '583ecae2-fb46-11e1-82cb-f4ce4684ea4c'}
