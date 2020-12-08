import QtQuick 2.0;
import calamares.slideshow 1.0;

Presentation
{
    id: presentation

    Timer {
        interval: 10000
        running: true
        repeat: true
        onTriggered: presentation.goToNextSlide()
    }
    Slide {
        Image {
            anchors.centerIn: parent
            id: image1
            x: 0
            y: 0
            width: 660
            height: 169
            source: "slide1.png"
        }
     }
    Slide {
        Text {
            id: text1
            x: 0
            y: 100
            width: 800
            height: 50
            color: "#333333"
            text: qsTr("TO UNDERSTAND THE CONCEPT, YOU SHOULD THINK OF FREE")
            verticalAlignment: Text.AlignTop
            horizontalAlignment: Text.AlignLeft
            textFormat: Text.AutoText
            font { family: "Ubuntu Light"; pixelSize: 18; weight: Font.Bold; capitalization: Font.AllUppercase }
        }
        Text {
            id: text2
            x: 0
            y: 140
            width: 800
            height: 50
            color: "#333333"
            text: qsTr("AS IN FREE SPEECH, NOT AS IN FREE BEER.")
            verticalAlignment: Text.AlignTop
            horizontalAlignment: Text.AlignLeft
            textFormat: Text.AutoText
            font { family: "Ubuntu Light"; pixelSize: 18; weight: Font.Bold; capitalization: Font.AllUppercase }
        }
    }
    Slide {
        Image {
            anchors.centerIn: parent
            id: image2
            x: 0
            y: 0
            width: 498
            height: 486
            fillMode: Image.PreserveAspectFit
            source: "slide2.png"
        }
    }
    Slide {
        Text {
            id: text3
            x: 0
            y: 100
            width: 800
            height: 50
            color: "#333333"
            text: qsTr("THE GNU OPERATING SYSTEM, IS THE ONLY OPERATING SYSTEM")
            verticalAlignment: Text.AlignTop
            horizontalAlignment: Text.AlignLeft
            textFormat: Text.AutoText
            font { family: "Ubuntu Light"; pixelSize: 18; weight: Font.Bold; capitalization: Font.AllUppercase }
        }
        Text {
            id: text4
            x: 0
            y: 140
            width: 800
            height: 50
            color: "#333333"
            text: qsTr("THAT WAS EVER DEVELOPED FOR ETHICAL REASONS,")
            verticalAlignment: Text.AlignTop
            horizontalAlignment: Text.AlignLeft
            textFormat: Text.AutoText
            font { family: "Ubuntu Light"; pixelSize: 18; weight: Font.Bold; capitalization: Font.AllUppercase }
        }
        Text {
            id: text5
            x: 0
            y: 180
            width: 800
            height: 50
            color: "#333333"
            text: qsTr("INSTEAD OF FOR COMMERCIAL OR TECHNICAL REASONS")
            verticalAlignment: Text.AlignTop
            horizontalAlignment: Text.AlignLeft
            textFormat: Text.AutoText
            font { family: "Ubuntu Light"; pixelSize: 18; weight: Font.Bold; capitalization: Font.AllUppercase }
        }
        
    }
    
    
    
    Slide {
        Image {
            anchors.centerIn: parent
            id: image3
            x: 0
            y: 0
            width: 675
            height: 384
            fillMode: Image.PreserveAspectFit
            source: "slide3.png"
        }
    }
     Slide {
        Text {
            id: text6
            x: 0
            y: 100
            width: 800
            height: 50
            color: "#333333"
            text: qsTr("FREIE SOFTWARE IST DER WEG AUS DER KOSTENINTENSIVEN")
            verticalAlignment: Text.AlignTop
            horizontalAlignment: Text.AlignLeft
            textFormat: Text.AutoText
            font { family: "Ubuntu Light"; pixelSize: 18; weight: Font.Bold; capitalization: Font.AllUppercase }
        }
        Text {
            id: text7
            x: 0
            y: 140
            width: 800
            height: 50
            color: "#333333"
            text: qsTr("ABHÄNGIGKEIT DER SCHULEN VON EINZELNEN FIRMEN.")
            verticalAlignment: Text.AlignTop
            horizontalAlignment: Text.AlignLeft
            textFormat: Text.AutoText
            font { family: "Ubuntu Light"; pixelSize: 18; weight: Font.Bold; capitalization: Font.AllUppercase }
        }
    }
    
    
    
    Slide {
        Image {
            anchors.centerIn: parent
            id: image4
            x: 150
            y: 0
            width: 299
            height: 399
            source: "slide4.png"
        }
    }
    
    Slide {
        Text {
            id: text8
            x: 0
            y: 100
            width: 800
            height: 50
            color: "#333333"
            text: qsTr("UNABHÄNGIGKEIT UND SOFTWARE-VIELFALT SOWIE DIE VERWENDUNG ")
            verticalAlignment: Text.AlignTop
            horizontalAlignment: Text.AlignLeft
            textFormat: Text.AutoText
            font { family: "Ubuntu Light"; pixelSize: 18; weight: Font.Bold; capitalization: Font.AllUppercase }
        }
        Text {
            id: text9
            x: 0
            y: 140
            width: 800
            height: 50
            color: "#333333"
            text: qsTr("OFFENER STANDARDS BIETEN EINE BASIS FÜR IT-SICHERHEIT.")
            verticalAlignment: Text.AlignTop
            horizontalAlignment: Text.AlignLeft
            textFormat: Text.AutoText
            font { family: "Ubuntu Light"; pixelSize: 18; weight: Font.Bold; capitalization: Font.AllUppercase }
        }
    }
    
    
    
    
    
}
