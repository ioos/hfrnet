
/*
 *
 * - "HFRNet - Focused exclusively on the to be system, eliminate HFRNet v1.0 nomenclature and assumptions.
 *  System Landscape and System Context" 
*/
workspace "HFRNet" "Workspace for HFRNet system architecture." {

    model {
        hfrSite = softwareSystem "HFR Site" "An HFR Station where a SeaSonde/WERA/LERA unit is installed and operating." {
            tags "HFRSite"
        }
        hfrUser = person "HFR User" "A person (or system) that uses HFR derived products." {
            tags "User"
        }
        hfrOperator = person "Site Operator" "A person responsible for configuring and maintaining a site." {
            tags "User"
        }
/* container <name> [description] [technology] [tags] {
 *   ...
 * }
 * 
 * softwareSystem <name> [description] [tags] {
 *    ...
 * }
*/
        hfrnetSS = softwaresystem "HFRNet" "Aggregate raw data and process into useful outputs for dissemination." {
            tags "HFRNetSS"
            
            siteAggregator = container "Site Aggregator" "Portal(s) to aggregate raw data from sites." "Python/Shell" {
                tags "internal"
                aggregatorMonitor = Component "Aggregator Monitor" "Monitor and report site health metrics and site configuration." "Python/Shell" {
                tags "internal"
                }
            }   
            aggregatorDB  = container "Site Aggregator Database" "Maintain site configuration and [RESEARCH THIS]" "MySQL" {
                tags "database"
            }
            // TODO: Look at the NCCF slides and update node to be consistent with their terminology (proddev?)
            prod = container "Product Dev" "Collect data from Site Aggregators and process raw data into products." {
                tags "internal"
                prodDissemination = Component "Egress" "Method to egress product files from production." "FTP or S3" {
                tags "internal"
                }
                prodLogic = Component "Product Logic" "Scripts to orchestrate computations and data dissemination." "Python/Shell" {
                tags "internal"
                }
                waveCalc = Component "Waves" "Matlab toolbox to calculate wave parameters from radial data." "Matlab to Python" {
                tags "internal"
                }
                rtvCalc = Component "RTV" "Matlab toolbox to calculate Total Vectors from radial data." "Matlab to Python" {
                tags "internal"
                }
                prodMonitor = Component "Prod Monitor" "Monitor and report system health metrics (e.g. 80/80)." "Python/Shell" {
                tags "internal"
                }
                prodLogic -> rtvCalc "Orchestrate RTV calculation and I/O"
                prodLogic -> waveCalc "Orchestrate waves calculation and I/O"
                prodLogic -> prodMonitor "Calculate metrics"
                prodLogic -> prodDissemination "Stages files for Egress"
            }
            prodDB = container "Product Database" "Product database containing site configuration and data flow metrics." "MySQL" {
                tags "database"
            }
        } // End hfrnet softwaresystem

        // External Systems
        hfrnetWebsite = softwareSystem "System status website" "Services that provides visualizations of products and metrics; manages site configuration." "html, OpenMaps, Javascript." {
            tags "website"
        }
        dissemination = softwareSystem "Operational Dissemination" "Retrieve files from Egress, reformat, and distribute." {
            archiver = container "Archiver" "Create archive packages and send to NCEI."
            reformatter = Container "Reformatter" "Convert from netCDF to GTS formats"
            distributor = Container "Distributor" "Push data to NWSTG via ftpsin 421"
            thredds = Container "THREDDS Data Server" "Service to organize and publish products (e.g RTV) to customers, including NOAA Operations." "OPeNDAP, OGC/WMS (ncWMS), other APIs"  
            tags "external"
        }
        nwstg = softwaresystem "NWSTG" "NWS managed gateway to the WMO GTS for international dissemination." {
            tags "external"
        }
        data_tanks = softwaresystem "NCEP Data Tank" "Datastore (/dcom) available to the NOAA Operational compute system WCOSS2." {
            tags "external"
        }
        archive = softwaresystem "NCEI Archive" "NCEI Archive for public dissemination." {
            tags "external"
        }
        radials_erddap = softwaresystem "ERDDAP" "ERRDAP server providing access to radial data files."{
            tags "external"
        }
        pda = softwaresystem "PDA" "NESDIS Product Dissemination A???" {
            tags "external"
        }

        // Define relationships container/container
        /* <identifier> -> <identifier> [description] [technology] [tags] {
         *    ...
         * }
        */
        hfrSite -> hfrnetSS "Provides data."
        hfrnetSS -> hfrUser "Uses products."
        hfrOperator -> hfrnetWebsite "Configure site"

        // Container to Container relationships
        siteAggregator -> hfrSite "Aggregates radials/configuration"
        prod -> siteAggregator "Pulls data from"
        prod -> prodDB "Query/update configuration and metrics." "TCP/SQL"
        siteAggregator -> aggregatorDB "Query/update site configuration."
        hfrnetWebsite -> aggregatorMonitor "Query/update site configuration."
        hfrnetWebsite -> prodMonitor "Pull metrics for visualization."
        hfrnetWebsite -> thredds "Access OGC/WMS API access to visualize maps."
        prod -> pda "Push products to"
        dissemination -> pda  "Retrieve files from PDA"
        dissemination -> archive "Publish monthly archive packages."

        // Fang Weng NDBC to NCEP via ftpsin line 421 is one route of getting hfr to the TG (IDP Dataflow team (nco.idp.dataflow@noaa.gov))
        dissemination -> nwstg "Provide [type?] files to NWSTG via Line ftpsin 421." "FTP"
        data_tanks -> thredds "Access OPeNDAP to populate data tanks via wget." "Shell/wget"
        radials_erddap -> dissemination  "Retrieve radials" "FTP"

        
        // Missing relationship between NDBC to WCOSS and/or NCEP data tanks via ncep decoders team (Fang Weng email)

        // Deployment Environments
        nccf = deploymentEnvironment "NCCF" {
            deploymentNode "NCCF Processing" {
                prodInstance = containerInstance prod
                siteAggregatorInstance = containerInstance siteAggregator
                prodDBInstance = containerInstance prodDB
                aggregatorDBInstance = containerInstance aggregatorDB
                
            }
            deploymentNode "Partner Web Hosting" {
                websiteInstance = softwareSystemInstance hfrnetWebsite
            }   
        } // End Deployment Environment CORDC

        disseminationDeployment = deploymentEnvironment "NDBC" {
            deploymentNode "NDBC Dissemination" {
                disseminationInstance = softwareSystemInstance dissemination
            }
            deploymentNode "NDBC THREDDS" {
                threddsInstance = containerInstance thredds
            }
        }  // End Deployment Environment NDBC

    } // End model

    // Views
    views {
        // System Context View starting point
        systemContext hfrnetSS "HFRNetSystemContext" {
            include *
            autoLayout lr
        }

        // System Landscape View More comprehensive freeform view of where it fits with other external entities
        systemLandscape hfrnetSSLandscape "HFRNet System Landscape" {
            include *
            autolayout lr
        }

        // Container View
        container hfrnetSS "HFRNetContainerView" {
            include *
            autolayout lr
        }
        // Component Views
        component prod "ProductDevelopmentServer" {
            include *
            autoLayout lr
        }

        // Deployment View at NCCF
        deployment hfrnetSS "NCCF" "NCCFProcessing" {
            include *
            autolayout lr
        }
        // Deployment View at NDBC
        deployment hfrnetSS "NDBC" {
            include *
            autolayout lr
        }


        // Element Styles For internal containers #87CEEB
/* element <tag> {
    shape <Box|RoundedBox|Circle|Ellipse|Hexagon|Cylinder|Pipe|Person|Robot|Folder|WebBrowser|MobileDevicePortrait|MobileDeviceLandscape|Component>
    icon <file|url>
    width <integer>
    height <integer>
    background <#rrggbb|color name>
    color <#rrggbb|color name>
    colour <#rrggbb|color name>
    stroke <#rrggbb|color name>
    strokeWidth <integer: 1-10>
    fontSize <integer>
    border <solid|dashed|dotted>
    opacity <integer: 0-100>
    metadata <true|false>
    description <true|false>
    properties {
        name value
    }
}
 */        
        styles {
            element "User" {
                shape Robot
            }
            element "hfrSite" {
                shape Robot
                background #55D6F8
            }
            element "HFRNetSS" {
                background #1E2D78
                color white
                shape RoundedBox
            }
            element "internal" {
                background #87CEEB
                shape RoundedBox
            }
            element "website" {
                background #87CEEB
                shape WebBrowser
            }
            element "database" {
                background #87CEEB
                shape Cylinder
            }
            element "external" {
                background #d3d3d3
                shape RoundedBox
            }

        } // End Element Styles
    } // End views

} // End Workspace

 