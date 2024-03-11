#!/bin/sh
curl -X PUT -H "Content-Type: application/json" -d "{\"id\":\"B2\",\"formula\":\"6\"}" localhost:3000/cells/B2
curl -X PUT -H "Content-Type: application/json" -d "{\"id\":\"B3\",\"formula\":\"7\"}" localhost:3000/cells/B3
curl -X PUT -H "Content-Type: application/json" -d "{\"id\":\"D4\",\"formula\":\"B2 * B3\"}" localhost:3000/cells/D4
