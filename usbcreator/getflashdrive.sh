#!/bin/bash
# by: thomas michael weissel
# you may use and alter this script - please report fixes and enchancements to valueerror@gmail.com 
# or to the google+ community "Free Open Source Software in Schools"
#
#   this bashscript is started via usbcreator.py which collects all the neccesary information
#
#  ./getflashdrive.sh",str(method),str(item.sharesize), str(copydata), str(item.id), str(iteminfo), str(update), str(self.isolocation) 
#   
#   method:  copy / iso / check
#   sharesize:   500 / 1000 / 8000 
#   copydata:  True / False
#   item.id:   sda / sdb / sdc
#   iteminfo:   adata s102 
#   update:    True / False
#   self.isolocation:   PathToIsoFile /home/student/life.iso
#
#



DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"   #directory of this script
USER=$(logname)   #logname seems to always deliver the current xsession user - no matter if you are using SUDO

#---------------------------------------------------------#"
#      get size of usb device                             #"
#---------------------------------------------------------#"  
getsizeInGB(){  ## get and display size of flashdrive to give the user more information about the found device
    USBBYTESIZE=$(lsblk -d -o SIZE  -n -r -b /dev/${USB}) 
    USBSIZE=$( expr ${USBBYTESIZE} / 1024 / 1024)
}
#---------------------------------------------------------#"
#      check for lockfiles - delete if not use            #"
#---------------------------------------------------------#"  
check(){  #tests for lock files and process threads - removes unnesessary lockfiles 
    if test -f ${DIR}/${USB}.lock;
    then 
        # test if there is a reason for the other lockfile
        PROCESS=$( pidof -x $0)   #test if there is a reason for lock files (another clone process) PIPING this throug "wc -w" would start another proces of this script for an instant
        PROCESS=$( wc -w <<< "$PROCESS")   # therefore we make it a two step process... no pipe..  don't know why this is neccesary but it works
        
        DEV=$( ls /dev/${USB} 2> /dev/null| wc -l )
        
        
        if [[( $PROCESS = "1" || $DEV != "1" )]]   ##no other process of this script is running and locked device not found in /dev
        then
        # echo "DELETE LOCK FILE"
            sudo rm *.lock > /dev/null 2>&1
            sudo umount -f mnt* > /dev/null 2>&1
            sudo rmdir mnt* > /dev/null 2>&1
        fi
    fi
}







#---------------------------------------------------------#"
#      SEARCH FOR DEVICE      START                       #"
#---------------------------------------------------------#"  
if  [[( $1 = "check" ) ]]
then
    #---------------------------------------------------------#"
    #   set the usb device a target for the clone process     #"
    #---------------------------------------------------------#"  
    settargetdevice(){
        # diese funktion überprüft zuerst ob das laufende system ein live system ist
        # danach wird geprüft ob es sich bei dem gefundenen usb stick vielleicht um den system datenträger handelt
        # ist alles ok kann die geräte information in die device lock.file geschrieben werden - diese info wird vom python programm ausgelesen
        ISCOW=$(df -h |grep cow |wc -l)
        ISAUFS=$(df -h |grep aufs |wc -l)
        if [[( $ISCOW = "0" ) && ( $ISAUFS = "0" ) && ( $COPYLIFE = "True" ) ]];
        then
            touch ${DIR}/${USB}.lock 
            printf "$USB;NOLIVE"  #dies ist kein live system.. usbkopie von installierten systemen nicht möglich  (ausser von ISO dateien)
            exit 0
        fi
        SYSMOUNT1=$(findmnt -nr -o target -S /dev/${USB}1)          #on the masterflashdrive (created from life.iso) this would be the systempartition
        SYSMOUNT2=$(findmnt -nr -o target -S /dev/${USB}2)          #on the final life flashdrive (created from this script) this would be the systempartition
        SYSMOUNT3=$(findmnt -nr -o target -S /dev/${USB})           #etcher creates a live usb device with no partition number
        
        if [[( $SYSMOUNT1 = '/cdrom' ) ||( $SYSMOUNT2 = '/cdrom' ) ||( $SYSMOUNT3 = '/cdrom' ) ]]                  ## check if this is the system device - check mountpoint!!
        then
            touch ${DIR}/${USB}.lock 
            printf "$USB;SYSUSB"    # der gefundene stick ist das systemdevice
            exit 0
        fi
        touch ${DIR}/${USB}.lock     #set target device
        SDX="/dev/$USB" 
        printf "$USB;$DEVICEVENDOR;$DEVICEMODEL;$DEVICESIZE;$USBBYTESIZE"
    }
    #---------------------------------------------------------#"
    #                 DETECTING USB DEVICE                    #"
    #---------------------------------------------------------#"
    #N=1
    #CHECKAGAIN=0
    USB=$2     ## Popen(["./getflashdrive.sh","check", dev ]   $1 = check $2 = dev (sda)  $3 = copylife (True)
    COPYLIFE=$3
    
    findusb(){
        #  check if proposed usb device is actually a usb device
        DEVICETYPE=$(lsblk -n -o TRAN /dev/$USB |grep usb|awk '{print $1;}')
        if [[ ( $DEVICETYPE = "usb" ) ]];   #check lsblk if this is really a usb device
        then
            DEVICEVENDOR=$(lsblk -n -o TRAN,VENDOR /dev/$USB |grep usb|awk '{print $2;}')
            DEVICEMODEL=$(lsblk -n -o TRAN,MODEL /dev/$USB |grep usb|awk '{print $2;}')
            DEVICESIZE=$(lsblk -n -o TRAN,SIZE /dev/$USB |grep usb|awk '{print $2;}')
            USBBYTESIZE=$(lsblk -d -o SIZE  -n -r -b /dev/${USB}) 
            settargetdevice
        else
            printf "$USB;NOUSB"   #kein usb stick gefunden bzw. alle bereits in arbeit
        fi
    }
    
    DEV=$( ls /dev/${USB} 2> /dev/null | wc -l )
    if [[( $DEV = "1" )]]   ##  device  found in /dev
    then
        findusb
    else
        printf "$USB;NOUSB"    #kein usb stick gefunden
    fi

fi
#---------------------------------------------------------#"
#      SEARCH FOR DEVICE      END                         #"
#---------------------------------------------------------#" 












#---------------------------------------------------------#"
#      PREPARE DEVICE      START                          #"
#---------------------------------------------------------#" 
if  [[( $1 = "copy" ) || ( $1 = "iso" )  ]]
then
    LIFESIZE="4000"    #darf nicht grösser sein. fat32 beschränkung für squashfs datei
    SHARESIZE=$2
    COPYCASPER=$3
    USB=$4
    TITLE=$5
    UPDATE=$6
    ISOFILE=$7
    
    TITLE=${TITLE//[-]/ }
    SDX="/dev/$USB" 
    
    #UPDATE="True"   skip formatting
    
    #---------------------------------------------------------#"
    #     start partitioning usb device                       #"
    #---------------------------------------------------------#"  
    partitiondevice(){

        LIFESIZEEND=$(( $SHARESIZE + $LIFESIZE ))
        
        # Ensuring that the device is not mounted #
        sudo umount ${SDX}1 > /dev/null 2>&1  #hide output
        sudo umount ${SDX}2 > /dev/null 2>&1  #hide output
        sudo umount ${SDX}3 > /dev/null 2>&1  #hide output

        ##############1
        echo "Part. Tabelle erstellen" 
        sleep 0.5
        ############## 
        
        sudo partprobe $SDX  > /dev/null 2>&1  #hide output
        sudo parted -s $SDX mklabel MSDOS  > /dev/null 2>&1  #hide output
        
        
        ##############2
        echo "Partitionen erstellen" 
        sleep 0.5
        ##############
        
     

        sudo partprobe $SDX  > /dev/null 2>&1  #hide output
        sudo parted -s $SDX mkpart primary 0% $SHARESIZE  > /dev/null 2>&1  #hide output
        sudo parted -s $SDX mkpart primary $SHARESIZE $LIFESIZEEND  > /dev/null 2>&1  #hide output
        sudo parted -s $SDX mkpart primary $LIFESIZEEND 100%  > /dev/null 2>&1  #hide output
 
        # Setting boot flag to second partition   #
        sudo parted -s $SDX set 2 boot on  > /dev/null 2>&1  #hide output
        sudo parted -s $SDX print  > /dev/null 2>&1  #hide output
        


        ##############3
        echo "Synchronisiere Daten" 
        sleep 2
        ##############



        sudo partprobe $SDX  > /dev/null 2>&1  #hide output

        
        ##############4
        echo "Dateisysteme erstellen" 
        sleep 0.5
        ##############
        
        ##############5
        echo "Erstelle Share (fat32)" 
        sleep 0.5
        ##############
        sudo mkfs.vfat -F 32 -n SHARE ${SDX}1 > /dev/null 2>&1  #hide output
        sleep 0.5
        
        
        ##############6
        echo "Erstelle Lifeclient (fat32)" 
        sleep 0.5
        ##############
        sudo mkfs.vfat -F 32 -n LIFECLIENT ${SDX}2 > /dev/null 2>&1  #hide output
        sleep 0.5
        
        
        ##############7
        echo "Erstelle Casper-rw  (ext4)" 
        sleep 0.5
        ##############
        #trying ext2 because a journalling fs on a flashdrive is probably to heavy
        sudo mkfs.ext4 -L casper-rw ${SDX}3 > /dev/null 2>&1  #hide output
        
        
        ##############8
        echo "Dateisysteme einlesen" 
        sleep 0.5
        ##############
        sleep 1
        #sudo mkfs.ext2 -b 4096 -L home-rw ${SDX}3
        sudo partprobe  > /dev/null 2>&1  #hide output

        #  teste ob paritionierung erfolgreich war
        checkpart
    }

    
    PCOUNT="0"
    
    checkpart(){
        ##############9
        echo "Prüfe Partitionen" 
        sleep 0.5
        ##############
    
        ISLIVE=$(sudo mlabel -si /dev/${USB}2 |awk '{print $4}') 
        if [[ ( "$ISLIVE" = "LIFECLIENT" ) ]];   #check if string not empty or null  (if life usb is found this ISLIVE returns a line
        then
            ##############10
            echo "Partitionierung ok" 
            sleep 0.5
            ##############
            
        else
            if [[( $PCOUNT = "0"  )]]   # try a second time before failing
            then
                PCOUNT="1"
                ##############10
                echo "Partitionierung fehlerhaft" 
                sleep 1
                echo "Starte Partitionierung erneut"
                sleep 1
                ##############
                
                partitiondevice
            else
                check
                ##############10
                echo "FAILED" 
                sleep 0.5
                ##############
                exit 0
            fi
        fi
    }
    
    

    ## IF update -  no partitioning  - check partitions and sync system 
    
    if [[( $UPDATE = "True"  )]]
    then
        ISLIVE=$(sudo mlabel -si /dev/${USB}2 |awk '{print $4}') 
        if [[  ( "$ISLIVE" = "LIFECLIENT" ) ]];   #check if string not empty or null  (if life usb is found this ISLIVE returns a line
        then
            ##############11
            echo "Erhalte alte Partitionen" 
            sleep 1.5
            ##############
            ONLYUPDATE="true"
        else
            ##############11
            echo "Erstelle neue Partitionen" 
            sleep 0.5
            ##############
            ONLYUPDATE="false"
            partitiondevice
        fi
    else
        ##############11
        echo "Erstelle neue Partitionen" 
        sleep 0.5
        ##############
        ONLYUPDATE="false"
        partitiondevice
    fi
    
   

    
    
    mountsystempartition(){   ## this function tests if the mount directory already exists and creates a mount directory with a unique name
        
        ##############12
        echo "Erstelle Mountpoint" 
        sleep 0.5
        ##############
        MOUNTPOINT="mnt"
        count=0
        
        while [ -d $MOUNTPOINT ]   #we are doing this because another clone process could be active and already captured mnt
        do
            # MOUNTPOINT="mnt${count}"
            #echo "$MOUNTPOINT directory already exists!"
            (( count++ ))
            MOUNTPOINT="mnt${count}"
            #echo "testing $MOUNTPOINT ..."
        done
        #echo ""
        #echo "#--------------------------------#"
        #echo "# Creating directory $MOUNTPOINT !      #"
        #echo "#--------------------------------#"
        #echo ""
        sudo mkdir $MOUNTPOINT
            
            
            
        ##############13
        echo "USB Stick wird eingebunden" 
        sleep 0.5
        ##############
        sudo mount ${SDX}2  $MOUNTPOINT
    }
    mountsystempartition  
    
    
    
    if [[ ( ${ONLYUPDATE} = "true" ) ]];
    then
        sudo rm -r $MOUNTPOINT/boot/*   > /dev/null 2>&1  #hide output
        sudo rm -r $MOUNTPOINT/casper/*   > /dev/null 2>&1  #hide output
        sudo rm -r $MOUNTPOINT/EFI/*   > /dev/null 2>&1  #hide output
        sudo rm -r $MOUNTPOINT/syslinux/*   > /dev/null 2>&1  #hide output
    fi
    
    
    
    
    if  [[( $1 = "iso" ) ]]  
    then
        sudo mount -o loop $ISOFILE /cdrom
    fi
    
    FILENUMBER=$(ls -Rahl /cdrom/ |wc -l)
    ##############
    echo "FILENUMBER,$FILENUMBER"   #send keyword and filenumber to python program
    ##############
    
    ##############14
    echo "Kopiere Systemdateien" 
    sleep 0.5
    ##############
    sudo rsync -a -h --info=progress2,stats --no-inc-recursive /cdrom/ $MOUNTPOINT | stdbuf -oL tr '\r' '\n' | stdbuf -oL tr -s " " | stdbuf -oL cut -d " " -f 2-4
    

    
    
    
    
    ##############15
    echo "Bootloader Konfiguration" 
    sleep 0.5
    ##############
    #just in case the script is run off a live dvd or virtualbox
    if [ -d ${MOUNTPOINT}/isolinux/ ];
    then
        sudo mv ${MOUNTPOINT}/isolinux/ ${MOUNTPOINT}/syslinux/   > /dev/null 2>&1  #hide output
    fi
    sudo cp ${DIR}/syslinux/* ${MOUNTPOINT}/syslinux/   > /dev/null 2>&1  #hide output
    sudo cp ${DIR}/grub/* ${MOUNTPOINT}/boot/grub/  > /dev/null 2>&1  #hide output



    ##############16
    echo "Synchronisiere Daten" 
    sleep 0.5
    ##############
    sudo sync    > /dev/null 2>&1  #hide output  # dauert ewig..  notwendig ?????????  JEIN! wird sonst vor "install bootloader automatisch nachgeholt und verwirrt



    ##############17
    echo "Installiere Bootloader" 
    sleep 0.5
    ##############
    sudo syslinux -if -d /syslinux ${SDX}2
    sleep 3
    sudo install-mbr ${SDX}
    



    
    
    #---------------------------------------------------------#"
    #      also copy casper-rw partition                      #"
    #---------------------------------------------------------#" 
    if [[( $COPYCASPER = "True"  )]]
    then
        
        ##############18
        echo "Kopiere Datenpartition" 
        sleep 0.5
        ##############
        
        
        ##############19
        echo "Zielpartition einhängen" 
        sleep 0.5
        ##############
        sudo sync
        sudo umount $MOUNTPOINT > /dev/null 2>&1 
        sudo umount -l $MOUNTPOINT > /dev/null 2>&1 
        sudo umount -f $MOUNTPOINT > /dev/null 2>&1    #we make sure this sucker is umounted 
        sudo mount ${SDX}3  $MOUNTPOINT  #mount third partition casper-rw
        
        
        ##############20
        echo "Datenpartition einhängen" 
        sleep 0.5
        ##############
        MOUNTPOINTCASPER="casper-rw"
        count=0
        while [ -d $MOUNTPOINTCASPER ]   #just in case another clone process is also using this mountpoint
        do
            MOUNTPOINTCASPER="casper-rw${count}"
            #echo "$MOUNTPOINTCASPER directory already exists!"
            (( count++ ))
            MOUNTPOINTCASPER="casper-rw${count}"
            #echo "testing $MOUNTPOINTCASPER ..."
        done
        sudo mkdir $MOUNTPOINTCASPER
        
        #  Detecting and mounting cow device - current systemdevice #
        COW=$(cat /proc/mounts | grep /cdrom | /bin/sed -e 's/^\/dev\/*//' |cut -c 1-3)   #find cow device
        COWDEV="/dev/${COW}3"   #the current casper partition
        
        sudo mount $COWDEV $MOUNTPOINTCASPER
        
        
        ##############21
        echo "Temporäre Dateien löschen" 
        sleep 0.5
        ##############
        sudo apt-get clean
        sudo apt-get autoclean
        sudo rm /home/${USER}/.kde/share/apps/RecentDocuments/* > /dev/null 2>&1 
        sudo rm -r /var/tmp/kdecache-${USER}/* > /dev/null 2>&1 
        sudo rm -r /home/${USER}/.cache > /dev/null 2>&1 
        history -w
        history -c
        
        
        ##############22
        echo "Benutzerdaten übertragen" 
        sleep 0.5
        ##############

        FILENUMBER=$(ls -Rahl ${MOUNTPOINTCASPER}/ |wc -l)
        ##############
        echo "CASPER,$FILENUMBER"   #send keyword and filenumber to python program
        ##############

        rsync -a -h --info=progress2,stats --no-inc-recursive ${MOUNTPOINTCASPER}/ $MOUNTPOINT | stdbuf -oL tr '\r' '\n' | stdbuf -oL tr -s " " | stdbuf -oL cut -d " " -f 2-4
        
        
        ##############23
        echo "Partitionen aushängen" 
        sleep 0.5
        ##############
        # remove casper mountpoint
        sudo umount $MOUNTPOINTCASPER > /dev/null 2>&1
        sudo umount -l $MOUNTPOINTCASPER > /dev/null 2>&1  #hide errors
        sudo rmdir $MOUNTPOINTCASPER > /dev/null 2>&1

    fi
    
    check   #remove lock files and mount points

    ##############18/24
    echo "END" 
    
    ##############
fi
#---------------------------------------------------------#"
#      PREPARE DEVICE      END                            #"
#---------------------------------------------------------#" 

































