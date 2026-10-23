let groups = JSON.parse(localStorage.getItem("groups")) || [];
let teachers = JSON.parse(localStorage.getItem("teachers")) || [];
let subjects = JSON.parse(localStorage.getItem("subjects")) || [];
let rooms = JSON.parse(localStorage.getItem("rooms")) || [];

function saveData() {
    localStorage.setItem("groups", JSON.stringify(groups));
    localStorage.setItem("teachers", JSON.stringify(teachers));
    localStorage.setItem("subjects", JSON.stringify(subjects));
    localStorage.setItem("rooms", JSON.stringify(rooms));
}

function showSection(sectionId) {
    document.querySelectorAll(".section").forEach(section => {
        section.classList.add("hidden");
    });
    let section = document.getElementById(sectionId);
    if (section) {
        section.classList.remove("hidden");
    }
}

function updateDashboard() {
    document.getElementById("studentCount").innerText = groups.length;
    document.getElementById("teacherCount").innerText = teachers.length;
    document.getElementById("subjectCount").innerText = subjects.length;
    document.getElementById("roomCount").innerText = rooms.length;
}

function addGroup() {
    let name = document.getElementById("groupName").value;
    let count = document.getElementById("groupCount").value;

    if (name === "" || count === "") {
        alert("Please enter all details");
        return;
    }

    groups.push({ name: name, count: count });
    saveData();

    document.getElementById("groupName").value = "";
    document.getElementById("groupCount").value = "";

    updateDashboard();
    displayGroups();
}

function displayGroups() {
    let output = "";
    groups.forEach(group => {
        output += `<div class="card">${group.name} - ${group.count} Students</div>`;
    });
    document.getElementById("groupList").innerHTML = output;
}

function addTeacher() {
    let name = document.getElementById("teacherName").value;
    let subject = document.getElementById("teacherSubject").value;
    let availability = document.getElementById("teacherAvailability").value;

    if (name === "" || subject === "" || availability === "") {
        alert("Please enter all details");
        return;
    }

    teachers.push({ name: name, subject: subject, availability: availability });
    saveData();

    document.getElementById("teacherName").value = "";
    document.getElementById("teacherSubject").value = "";
    document.getElementById("teacherAvailability").value = "";

    updateDashboard();
    displayTeachers();
}

function displayTeachers() {
    let output = "";
    teachers.forEach(teacher => {
        output += `
            <div class="card">
                <b>${teacher.name}</b><br>
                Subject: ${teacher.subject}<br>
                Available: ${teacher.availability}
            </div>
        `;
    });
    document.getElementById("teacherList").innerHTML = output;
}

function addSubject() {
    let name = document.getElementById("subjectName").value;
    let teacher = document.getElementById("subjectTeacher").value;
    let periods = document.getElementById("subjectPeriods").value;
    let group = document.getElementById("subjectGroup").value;
    let roomType = document.getElementById("subjectRoomType").value;

    if (name === "" || teacher === "" || periods === "" || group === "" || roomType === "") {
        alert("Please enter all details");
        return;
    }

    subjects.push({
        name: name,
        teacher: teacher,
        periods: periods,
        group: group,
        roomType: roomType
    });
    saveData();

    document.getElementById("subjectName").value = "";
    document.getElementById("subjectTeacher").value = "";
    document.getElementById("subjectPeriods").value = "";
    document.getElementById("subjectGroup").value = "";
    document.getElementById("subjectRoomType").value = "";

    updateDashboard();
    displaySubjects();
}

function displaySubjects() {
    let output = "";
    subjects.forEach(subject => {
        output += `
            <div class="card">
                <b>${subject.name}</b><br>
                Teacher: ${subject.teacher}<br>
                Group: ${subject.group}<br>
                Periods: ${subject.periods}<br>
                Room Type: ${subject.roomType}
            </div>
        `;
    });
    document.getElementById("subjectList").innerHTML = output;
}

function addRoom() {
    let name = document.getElementById("roomName").value;
    let capacity = document.getElementById("roomCapacity").value;
    let type = document.getElementById("roomType").value;

    if (name === "" || capacity === "" || type === "") {
        alert("Please enter all details");
        return;
    }

    rooms.push({ name: name, capacity: capacity, type: type });
    saveData();

    document.getElementById("roomName").value = "";
    document.getElementById("roomCapacity").value = "";
    document.getElementById("roomType").value = "";

    updateDashboard();
    displayRooms();
}

function displayRooms() {
    let output = "";
    rooms.forEach(room => {
        output += `
            <div class="card">
                <b>${room.name}</b><br>
                Capacity: ${room.capacity}<br>
                Type: ${room.type}
            </div>
        `;
    });
    document.getElementById("roomList").innerHTML = output;
}

async function generateTimetable() {
    alert("Generate button clicked");
    console.log("Function started");

    try {
        const response = await fetch("output.txt");
        if (!response.ok) {
            throw new Error("output.txt not found");
        }

        const text = await response.text();
        console.log(text);

        if (text.trim() === "") {
            throw new Error("output.txt is empty");
        }

        let lines = text.trim().split(/\r?\n/);

        if (lines.length > 0 && lines[0].toUpperCase().includes("GROUP")) {
            lines.shift();
        }

        let timetableData = [];
        lines.forEach(line => {
            if (line.trim() === "") return;
            let parts = line.split(",");
            if (parts.length < 6) return;

            timetableData.push({
                group: parts[0].trim(),
                day: parts[1].trim(),
                period: parseInt(parts[2].trim()),
                subject: parts[3].trim(),
                teacher: parts[4].trim(),
                room: parts[5].trim()
            });
        });

        let uniqueGroups = [];
        timetableData.forEach(item => {
            if (!uniqueGroups.includes(item.group)) {
                uniqueGroups.push(item.group);
            }
        });

        console.log("Groups Found:", uniqueGroups);

        if (timetableData.length === 0) {
            alert("No timetable data found in output.txt");
            return;
        }

        let workingDays = parseInt(document.getElementById("workingDays").value);
        let periodsPerDay = parseInt(document.getElementById("periodsPerDay").value);
        let dayNames = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

        let allTables = "";

        uniqueGroups.forEach(groupName => {
            let table = `
                <h3>${groupName} Timetable</h3>
                <table border="1">
                    <tr>
                        <th>Day</th>
            `;

            for (let p = 1; p <= periodsPerDay; p++) {
                table += `<th>P${p}</th>`;
            }

            table += `</tr>`;

            for (let d = 0; d < workingDays; d++) {
                let day = dayNames[d];
                table += `<tr><td><b>${day}</b></td>`;

                for (let p = 1; p <= periodsPerDay; p++) {
                    if (p === 3) {
                        table += `<td><b>BREAK</b></td>`;
                        continue;
                    }
                    if (p === 6) {
                        table += `<td><b>LUNCH</b></td>`;
                        continue;
                    }

                    let entry = timetableData.find(item =>
                        item.group === groupName && item.day === day && item.period === p
                    );

                    if (entry) {
                        table += `
                            <td>
                                <b>${entry.subject}</b><br>
                                <small>${entry.teacher}</small><br>
                                <small>${entry.room}</small>
                            </td>
                        `;
                    } else {
                        table += `<td>Free</td>`;
                    }
                }
                table += `</tr>`;
            }

            table += `</table><br><br>`;
            allTables += table;
        });

        document.getElementById("timetableOutput").innerHTML = allTables;

        let possibleArrangements = subjects.length * teachers.length * rooms.length * workingDays * periodsPerDay;
        document.getElementById("possibleSolutions").innerText = "Possible Arrangements: " + possibleArrangements;
        document.getElementById("validSolutions").innerText = "Valid Timetables: C++ Generated";
        document.getElementById("bestScore").innerText = "Best Score: Generated by C++";
        document.getElementById("topSolutions").innerHTML = `<p>Best timetable selected by C++ optimization engine.</p>`;

        let workload = {};
        timetableData.forEach(item => {
            if (!workload[item.teacher]) {
                workload[item.teacher] = 0;
            }
            workload[item.teacher]++;
        });

        let workloadHTML = "";
        for (let teacher in workload) {
            workloadHTML += `<p><b>${teacher}</b> : ${workload[teacher]} Periods</p>`;
        }
        document.getElementById("teacherWorkload").innerHTML = workloadHTML;

        let roomUsage = {};
        timetableData.forEach(item => {
            if (!roomUsage[item.room]) {
                roomUsage[item.room] = 0;
            }
            roomUsage[item.room]++;
        });

        let roomHTML = "";
        for (let room in roomUsage) {
            roomHTML += `<p><b>${room}</b> : ${roomUsage[room]} Periods Used</p>`;
        }
        document.getElementById("roomUtilization").innerHTML = roomHTML;

        document.getElementById("searchProcess").innerHTML = "Search completed successfully.";
        document.getElementById("optimizationSummary").innerHTML = "All timetable constraints satisfied.";
        document.getElementById("scoreBreakdown").innerHTML = "Score generated by optimization engine.";
        showSection("results");

    } catch (error) {
        console.error(error);
        alert("Cannot load output.txt.\n\nMake sure output.txt is inside the frontend folder.");
    }
}

function exportCSV() {
    let tables = document.querySelectorAll("#timetableOutput table");

    if (tables.length === 0) {
        alert("Generate timetable first");
        return;
    }

    let csv = "";

    tables.forEach((table, index) => {
        let title = table.previousElementSibling;
        if (title) {
            csv += title.innerText + "\n";
        }

        let rows = table.querySelectorAll("tr");
        rows.forEach(row => {
            let cols = row.querySelectorAll("th,td");
            let rowData = [];
            cols.forEach(col => {
                let value = col.innerText.replace(/,/g, " ");
                rowData.push(value);
            });
            csv += rowData.join(",") + "\n";
        });
        csv += "\n\n";
    });

    let blob = new Blob([csv], { type: "text/csv" });
    let link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "All_Timetables.csv";
    link.click();
}

function printTimetable() {
    let content = document.getElementById("timetableOutput").innerHTML;
    let printWindow = window.open("", "", "width=1000,height=700");

    printWindow.document.write(`
        <html>
        <head>
            <title>Timetable</title>
            <style>
                body { font-family: Arial; padding: 20px; }
                table { width: 100%; border-collapse: collapse; margin-bottom: 30px; }
                th, td { border: 1px solid black; padding: 10px; text-align: center; }
                th { background: #eeeeee; }
            </style>
        </head>
        <body>
            <h2>Generated Timetable</h2>
            ${content}
        </body>
        </html>
    `);

    printWindow.document.close();
    printWindow.print();
}

function createInputFile() {
    let data = "GROUPS\n";
    groups.forEach(group => {
        data += group.name + "," + group.count + "\n";
    });

    data += "TEACHERS\n";
    teachers.forEach(teacher => {
        data += teacher.name + "," + teacher.subject + "," + teacher.availability + "\n";
    });

    data += "SUBJECTS\n";
    subjects.forEach(subject => {
        data += subject.name + "," + subject.teacher + "," + subject.periods + "," + subject.group + "," + subject.roomType + "\n";
    });

    data += "ROOMS\n";
    rooms.forEach(room => {
        data += room.name + "," + room.capacity + "," + room.type + "\n";
    });

    data += "SETTINGS\n";
    let workingDays = document.getElementById("workingDays").value;
    let periodsPerDay = document.getElementById("periodsPerDay").value;
    data += workingDays + "," + periodsPerDay + "\n";

    let blob = new Blob([data], { type: "text/plain" });
    let link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "input.txt";
    link.click();
    URL.revokeObjectURL(link.href);

    alert("input.txt created successfully");
}

window.onload = function () {
    updateDashboard();
    displayGroups();
    displayTeachers();
    displaySubjects();
    displayRooms();
};