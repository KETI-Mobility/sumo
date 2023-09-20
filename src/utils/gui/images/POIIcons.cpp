/****************************************************************************/
// Eclipse SUMO, Simulation of Urban MObility; see https://eclipse.dev/sumo
// Copyright (C) 2001-2023 German Aerospace Center (DLR) and others.
// This program and the accompanying materials are made available under the
// terms of the Eclipse Public License 2.0 which is available at
// https://www.eclipse.org/legal/epl-2.0/
// This Source Code may also be made available under the following Secondary
// Licenses when the conditions for such availability set forth in the Eclipse
// Public License 2.0 are satisfied: GNU General Public License, version 2
// or later which is available at
// https://www.gnu.org/licenses/old-licenses/gpl-2.0-standalone.html
// SPDX-License-Identifier: EPL-2.0 OR GPL-2.0-or-later
/****************************************************************************/
/// @file    POIIcons.cpp
/// @author  Pablo Alvarez Lopez
/// @date    Sep 2023
///
// Function that returns the icon for a certain POI
/****************************************************************************/
#include <config.h>

#include <utils/common/SUMOVehicleClass.h>
#include <utils/foxtools/fxheader.h>
#include <utils/gui/images/GUIIconSubSys.h>

#include "POIIcons.h"


// ===========================================================================
// member method definitions
// ===========================================================================

FXIcon*
POIIcons::getPOIIcon(const SUMOVehicleClass vc) {
    switch (vc) {
        case SVC_IGNORING:
            return GUIIconSubSys::getIcon(GUIIcon::POIICON_TREE);
        case SVC_PRIVATE:
            return GUIIconSubSys::getIcon(GUIIcon::POIICON_HOTEL);
        default:
            throw ProcessError(TL("Invalid POI"));
    }
}

/****************************************************************************/