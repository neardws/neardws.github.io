<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <title>Xincao Xu Profile</title>
    <style>
        /* 为带链接的文字定义样式 */
        a.no-underline {
            text-decoration: none; /* 去除下划线 */
        }

        /* 可选：当鼠标悬停时添加样式 */
        a.no-underline:hover {
            text-decoration: underline; /* 鼠标悬停时显示下划线 */
        }

        table.no-horizontal-lines {
            border-collapse: collapse;
        }

        table.no-horizontal-lines td, 
        table.no-horizontal-lines th {
            border: none;
        }

        .tight-padding {
            padding-right: 10px;
            padding-left: 10px;
        }

        #map {
            width: 450px;
            height: 220px;
        }
    </style>
    <script src="https://cdn.apple-mapkit.com/mk/5.x.x/mapkit.js"></script>
</head>
<body>
    <h2>Xincao Xu (许新操 or 許新操)</h2>
    <p>
        Xincao Xu, also known as Neil Xu, received his Ph.D. degree in Computer Science from the College of Computer Science at Chongqing University (<a href="https://www.cqu.edu.cn" class="no-underline">CQU</a>), Chongqing, China, in 2023. He previously earned his B.S. degree in Network Engineering from the School of Computer and Control Engineering at the North University of China (<a href="https://www.nuc.edu.cn" class="no-underline">NUC</a>), Taiyuan, China, in 2017. Dr. Xu is currently a Postdoctoral Research Fellow, working in cooperation with Prof. <a href="https://scholar.google.com/citations?user=IhjhNEEAAAAJ" class="no-underline">Shaohua Wan</a> at the Shenzhen Institute for Advanced Study, University of Electronic Science and Technology of China (<a href="https://www.uestc.edu.cn" class="no-underline">UESTC</a>), in Shenzhen. He has authored and co-authored more than 15 papers with total google scholar <a href='https://scholar.google.com/citations?user=DK5avZUAAAAJ'><img src="https://img.shields.io/endpoint?logo=Google%20Scholar&url=https%3A%2F%2Fcdn.jsdelivr.net%2Fgh%2FNeardws%2Fneardws.github.io@google-scholar-stats%2Fgs_data_shieldsio.json&labelColor=f6f6f6&color=9cf&style=flat&label=Citations"></a>.
    </p>

    <p>
        His research interests are primarily focused on several cutting-edge areas, including:
        <ul>
            <li>AI for Driving, covering aspects like heterogeneous information fusion, cooperative sensing, multimodal deep learning, and driving behavior control.</li>
            <li>Vehicular Networks, with a focus on cooperative transmission and computing, integrated sensing and communications, and resource allocation.</li>
            <li>Vehicular Cyber-Physical Systems, encompassing sensing, transmitting, modeling, and controlling.</li>
            <li>Edge Computing, emphasizing the offloading of communication, computing, and caching abilities from the cloud to the network edge.</li>
            <li>Deep Reinforcement Learning, including multi-agent DRL, hierarchical DRL, and the integration of DRL with other technologies such as game theory and evaluation algorithms.</li>
            <li>Game Theory, with a specific interest in potential games, matching, auctions, and related concepts.</li>
        </ul>
    </p>

    <table class="no-horizontal-lines" style="margin-left: auto; margin-right: auto;">
        <tr>
            <td>
                Contact Information: <br>
                Office Address: <br>
                Room 810, Building 3, YESUN Intelligent Community II, <br>
                Guanlan Street, Longhua District, <br>
                Shenzhen 518110, China <br>
                Phone: 
                <a href="tel:+1-6015648240" class="no-underline">click to call</a> <br>
                E-mail:   
                <em>xc</em>DOT<em>xu</em>AT<em>uestc</em>DOT<em>edu</em>DOT<em>cn</em> | <em>neard</em>DOT<em>ws</em>AT<em>gmail</em>DOT<em>com</em> 
            </td>
            <td>
                <div id="map"></div>
            </td>
        </tr>
    </table>

    <script>
        mapkit.init({
            authorizationCallback: function(done) {
                var xhr = new XMLHttpRequest();
                xhr.open("GET", "/services/jwt");
                xhr.addEventListener("load", function() {
                    done(this.responseText);
                });
                xhr.send();
            }
        });

        var Cupertino = new mapkit.CoordinateRegion(
            new mapkit.Coordinate(22.729006, 114.038955), // Update the coordinate for clarity
            new mapkit.CoordinateSpan(0.012, 0.012) // Adjust span for better visibility
        );
        var map = new mapkit.Map("map");
        map.region = Cupertino;
    </script>
</body>
</html>
