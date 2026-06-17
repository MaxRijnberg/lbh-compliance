from __future__ import annotations

from typing import TypedDict, List, Required

PortAbleResponseAttachmentslistItem = TypedDict(
    "PortAbleResponseAttachmentslistItem",
    {
        "contentType": str,
        "createdAt": Required[str],
        "externalUse": bool,
        "filename": Required[str],
        "isPda": bool,
        "path": str,
        "size": str,
        "url": Required[str],
    },
    total=False,
)

PortAbleResponseBunkerslistItemBunkertype = TypedDict(
    "PortAbleResponseBunkerslistItemBunkertype",
    {
        "id": str,
        "name": str,
    },
    total=False,
)

PortAbleResponseBunkerslistItemFueltype = TypedDict(
    "PortAbleResponseBunkerslistItemFueltype",
    {
        "id": str,
        "name": str,
        "order": int | float,
    },
    total=False,
)

PortAbleResponseBunkerslistItemFueltypeunit = TypedDict(
    "PortAbleResponseBunkerslistItemFueltypeunit",
    {
        "id": str,
        "name": str,
    },
    total=False,
)

PortAbleResponseBunkerslistItem = TypedDict(
    "PortAbleResponseBunkerslistItem",
    {
        "bunkerType": PortAbleResponseBunkerslistItemBunkertype,
        "fuelType": PortAbleResponseBunkerslistItemFueltype,
        "fuelTypeUnit": PortAbleResponseBunkerslistItemFueltypeunit,
        "quantity": int | float,
    },
    total=False,
)

PortAbleResponseCargoslistItemCargotype = TypedDict(
    "PortAbleResponseCargoslistItemCargotype",
    {
        "cargoType": str,
        "id": str,
        "name": str,
    },
    total=False,
)

PortAbleResponseCargoslistItemRoutetoCoords = TypedDict(
    "PortAbleResponseCargoslistItemRoutetoCoords",
    {
        "lat": int | float,
        "lng": int | float,
    },
    total=False,
)

PortAbleResponseCargoslistItemRoutetoCountryContinent = TypedDict(
    "PortAbleResponseCargoslistItemRoutetoCountryContinent",
    {
        "code": str,
        "name": str,
    },
    total=False,
)

PortAbleResponseCargoslistItemRoutetoCountry = TypedDict(
    "PortAbleResponseCargoslistItemRoutetoCountry",
    {
        "code": str,
        "continent": PortAbleResponseCargoslistItemRoutetoCountryContinent,
        "flag": str,
        "name": str,
    },
    total=False,
)

PortAbleResponseCargoslistItemRouteto = TypedDict(
    "PortAbleResponseCargoslistItemRouteto",
    {
        "coords": PortAbleResponseCargoslistItemRoutetoCoords,
        "country": PortAbleResponseCargoslistItemRoutetoCountry,
        "id": str,
        "isOperational": bool,
        "locode": str,
        "name": str,
        "visiblePortable": bool,
    },
    total=False,
)

PortAbleResponseCargoslistItemUnit = TypedDict(
    "PortAbleResponseCargoslistItemUnit",
    {
        "id": str,
        "name": str,
    },
    total=False,
)

PortAbleResponseCargoslistItem = TypedDict(
    "PortAbleResponseCargoslistItem",
    {
        "berthTerminalName": str,
        "cargoPurpose": None,
        "cargoType": PortAbleResponseCargoslistItemCargotype,
        "commencedDate": None,
        "confirmedOperation": bool,
        "id": str,
        "loadUnloadedCargo": int | float,
        "marketingNotification": None,
        "moloAmount": int | float,
        "quantity": int | float,
        "quantityType": int | float,
        "routeTo": PortAbleResponseCargoslistItemRouteto,
        "tillDate": None,
        "unit": PortAbleResponseCargoslistItemUnit,
    },
    total=False,
)

PortAbleResponseDaowner = TypedDict(
    "PortAbleResponseDaowner",
    {
        "account": str,
        "country": str,
        "invoiceCountry": None,
        "message": str,
        "name": Required[str],
    },
    total=False,
)

PortAbleResponseEmailoptionsItemRecipientlistEmailaddresslistItem = TypedDict(
    "PortAbleResponseEmailoptionsItemRecipientlistEmailaddresslistItem",
    {
        "email": str,
        "mailingType": int | float,
    },
    total=False,
)

PortAbleResponseEmailoptionsItemRecipientlist = TypedDict(
    "PortAbleResponseEmailoptionsItemRecipientlist",
    {
        "emailAddressList": List[
            PortAbleResponseEmailoptionsItemRecipientlistEmailaddresslistItem
        ],
        "emailGroupList": str,
        "name": str,
        "selected": bool,
    },
    total=False,
)

PortAbleResponseEmailoptionsItemSendingemailsblocksItem = TypedDict(
    "PortAbleResponseEmailoptionsItemSendingemailsblocksItem",
    {
        "id": str,
        "name": str,
        "order": int | float,
        "status": int | float,
    },
    total=False,
)

PortAbleResponseEmailoptionsItem = TypedDict(
    "PortAbleResponseEmailoptionsItem",
    {
        "emailType": int | float,
        "recipientList": PortAbleResponseEmailoptionsItemRecipientlist,
        "sendingEmailsBlocks": List[
            PortAbleResponseEmailoptionsItemSendingemailsblocksItem
        ],
        "subject": str,
    },
    total=False,
)

PortAbleResponseHusbandry = TypedDict(
    "PortAbleResponseHusbandry",
    {
        "account": str,
        "country": str,
        "invoiceCountry": None,
        "message": str,
        "name": Required[str],
    },
    total=False,
)

PortAbleResponseNor = TypedDict(
    "PortAbleResponseNor",
    {
        "description": str,
        "to": str,
    },
    total=False,
)

PortAbleResponseNoteslistItemEditedbyCountryContinent = TypedDict(
    "PortAbleResponseNoteslistItemEditedbyCountryContinent",
    {
        "code": str,
        "name": str,
    },
    total=False,
)

PortAbleResponseNoteslistItemEditedbyCountry = TypedDict(
    "PortAbleResponseNoteslistItemEditedbyCountry",
    {
        "code": str,
        "continent": PortAbleResponseNoteslistItemEditedbyCountryContinent,
        "flag": str,
        "name": str,
    },
    total=False,
)

PortAbleResponseNoteslistItemEditedbyCountryItemContinent = TypedDict(
    "PortAbleResponseNoteslistItemEditedbyCountryItemContinent",
    {
        "code": str,
        "name": str,
    },
    total=False,
)

PortAbleResponseNoteslistItemEditedbyCountryItem = TypedDict(
    "PortAbleResponseNoteslistItemEditedbyCountryItem",
    {
        "code": str,
        "continent": PortAbleResponseNoteslistItemEditedbyCountryItemContinent,
        "decimalNotation": int | float,
        "flag": str,
        "name": str,
    },
    total=False,
)

PortAbleResponseNoteslistItemEditedbyCustomfiltersItemFilterslistItem = TypedDict(
    "PortAbleResponseNoteslistItemEditedbyCustomfiltersItemFilterslistItem",
    {
        "comparison": str,
        "field": str,
        "value": List[str],
    },
    total=False,
)

PortAbleResponseNoteslistItemEditedbyCustomfiltersItemOrder = TypedDict(
    "PortAbleResponseNoteslistItemEditedbyCustomfiltersItemOrder",
    {
        "direction": int | float,
        "field": str,
    },
    total=False,
)

PortAbleResponseNoteslistItemEditedbyCustomfiltersItem = TypedDict(
    "PortAbleResponseNoteslistItemEditedbyCustomfiltersItem",
    {
        "filtersList": List[
            PortAbleResponseNoteslistItemEditedbyCustomfiltersItemFilterslistItem
        ],
        "name": str,
        "order": PortAbleResponseNoteslistItemEditedbyCustomfiltersItemOrder,
    },
    total=False,
)

PortAbleResponseNoteslistItemEditedby = TypedDict(
    "PortAbleResponseNoteslistItemEditedby",
    {
        "country": List[PortAbleResponseNoteslistItemEditedbyCountryItem],
        "customFilters": List[PortAbleResponseNoteslistItemEditedbyCustomfiltersItem],
        "email": str,
        "firstname": str,
        "hasNoPdaAccess": bool,
        "id": str,
        "lastname": str,
        "noExcelDownload": None,
        "userRole": int | float,
    },
    total=False,
)

PortAbleResponseNoteslistItem = TypedDict(
    "PortAbleResponseNoteslistItem",
    {
        "editedBy": PortAbleResponseNoteslistItemEditedby,
        "fao": None,
        "note": str,
        "subject": str,
    },
    total=False,
)

PortAbleResponseOtherpartieslistItem = TypedDict(
    "PortAbleResponseOtherpartieslistItem",
    {
        "account": str,
        "country": str,
        "invoiceCountry": None,
        "message": str,
        "name": Required[str],
    },
    total=False,
)

PortAbleResponsePdastatus = TypedDict(
    "PortAbleResponsePdastatus",
    {
        "totalAmountReceived": int | float,
        "totalAmountRequested": int | float,
    },
    total=False,
)

PortAbleResponsePortofcallContact = TypedDict(
    "PortAbleResponsePortofcallContact",
    {
        "address1": str,
        "address2": str,
        "address3": str,
        "city": str,
        "country": str,
        "email": str,
        "name": str,
        "office": str,
        "phoneNumber": str,
        "role": str,
        "zipcode": str,
    },
    total=False,
)

PortAbleResponsePortofcallCoords = TypedDict(
    "PortAbleResponsePortofcallCoords",
    {
        "lat": int | float,
        "lng": int | float,
    },
    total=False,
)

PortAbleResponsePortofcallCountryContinent = TypedDict(
    "PortAbleResponsePortofcallCountryContinent",
    {
        "code": str,
        "name": str,
    },
    total=False,
)

PortAbleResponsePortofcallCountry = TypedDict(
    "PortAbleResponsePortofcallCountry",
    {
        "code": str,
        "continent": PortAbleResponsePortofcallCountryContinent,
        "flag": str,
        "name": str,
    },
    total=False,
)

PortAbleResponsePortofcall = TypedDict(
    "PortAbleResponsePortofcall",
    {
        "contact": PortAbleResponsePortofcallContact,
        "coords": PortAbleResponsePortofcallCoords,
        "country": PortAbleResponsePortofcallCountry,
        "id": str,
        "isOperational": bool,
        "locode": str,
        "name": str,
        "visiblePortable": bool,
    },
    total=False,
)

PortAbleResponsePortablepartieslistItem = TypedDict(
    "PortAbleResponsePortablepartieslistItem",
    {
        "dynamicsId": str,
        "email": str,
        "id": None,
        "keywordsList": List[str],
        "name": Required[str],
        "webUsersList": str,
    },
    total=False,
)

PortAbleResponsePortcallresponsiblesItemCountryContinent = TypedDict(
    "PortAbleResponsePortcallresponsiblesItemCountryContinent",
    {
        "code": str,
        "name": str,
    },
    total=False,
)

PortAbleResponsePortcallresponsiblesItemCountryCurrency = TypedDict(
    "PortAbleResponsePortcallresponsiblesItemCountryCurrency",
    {
        "code": str,
        "id": str,
        "name": str,
    },
    total=False,
)

PortAbleResponsePortcallresponsiblesItemCountry = TypedDict(
    "PortAbleResponsePortcallresponsiblesItemCountry",
    {
        "code": str,
        "continent": PortAbleResponsePortcallresponsiblesItemCountryContinent,
        "currency": PortAbleResponsePortcallresponsiblesItemCountryCurrency,
        "decimalNotation": None,
        "flag": str,
        "id": None,
        "name": str,
    },
    total=False,
)

PortAbleResponsePortcallresponsiblesItemCustomfiltersItemFilterslistItem = TypedDict(
    "PortAbleResponsePortcallresponsiblesItemCustomfiltersItemFilterslistItem",
    {
        "comparison": str,
        "field": str,
        "value": List[str],
    },
    total=False,
)

PortAbleResponsePortcallresponsiblesItemCustomfiltersItemOrder = TypedDict(
    "PortAbleResponsePortcallresponsiblesItemCustomfiltersItemOrder",
    {
        "direction": int | float,
        "field": str,
    },
    total=False,
)

PortAbleResponsePortcallresponsiblesItemCustomfiltersItem = TypedDict(
    "PortAbleResponsePortcallresponsiblesItemCustomfiltersItem",
    {
        "filtersList": List[
            PortAbleResponsePortcallresponsiblesItemCustomfiltersItemFilterslistItem
        ],
        "name": str,
        "order": PortAbleResponsePortcallresponsiblesItemCustomfiltersItemOrder,
    },
    total=False,
)

PortAbleResponsePortcallresponsiblesItem = TypedDict(
    "PortAbleResponsePortcallresponsiblesItem",
    {
        "country": PortAbleResponsePortcallresponsiblesItemCountry,
        "customFilters": List[
            PortAbleResponsePortcallresponsiblesItemCustomfiltersItem
        ],
        "email": str,
        "firstname": str,
        "hasNoPdaAccess": bool,
        "lastname": str,
        "userRole": int | float,
    },
    total=False,
)

PortAbleResponsePrincipal = TypedDict(
    "PortAbleResponsePrincipal",
    {
        "account": str,
        "country": str,
        "invoiceCountry": None,
        "message": str,
        "name": Required[str],
    },
    total=False,
)

PortAbleResponsePurposecall = TypedDict(
    "PortAbleResponsePurposecall",
    {
        "code": str,
        "id": str,
        "name": str,
        "order": int | float,
    },
    total=False,
)

PortAbleResponseRecipientslistItemEmailaddresslistItem = TypedDict(
    "PortAbleResponseRecipientslistItemEmailaddresslistItem",
    {
        "anchored": bool,
        "arrived": bool,
        "berthed": bool,
        "email": str,
        "expected": bool,
        "intransit": bool,
        "mailingType": int | float,
        "sailed": bool,
    },
    total=False,
)

PortAbleResponseRecipientslistItem = TypedDict(
    "PortAbleResponseRecipientslistItem",
    {
        "emailAddressList": List[
            PortAbleResponseRecipientslistItemEmailaddresslistItem
        ],
        "emailGroupList": str,
        "name": str,
        "selected": bool,
    },
    total=False,
)

PortAbleResponseRemarkslistItem = TypedDict(
    "PortAbleResponseRemarkslistItem",
    {
        "id": str,
        "includeSOF": bool,
        "name": str,
        "remark": str,
    },
    total=False,
)

PortAbleResponseSofsettings = TypedDict(
    "PortAbleResponseSofsettings",
    {
        "addBunkers": bool,
        "addDrafts": bool,
        "addNextPort": bool,
    },
    total=False,
)

PortAbleResponseStatus = TypedDict(
    "PortAbleResponseStatus",
    {
        "name": str,
    },
    total=False,
)

PortAbleResponseStowageplan = TypedDict(
    "PortAbleResponseStowageplan",
    {
        "cargoHoldsList": str,
        "remark": str,
        "type": int | float,
    },
    total=False,
)

PortAbleResponseSubstatus = TypedDict(
    "PortAbleResponseSubstatus",
    {
        "name": str,
    },
    total=False,
)

PortAbleResponseTodoslistItemEditedbyCountryContinent = TypedDict(
    "PortAbleResponseTodoslistItemEditedbyCountryContinent",
    {
        "code": str,
        "name": str,
    },
    total=False,
)

PortAbleResponseTodoslistItemEditedbyCountry = TypedDict(
    "PortAbleResponseTodoslistItemEditedbyCountry",
    {
        "code": str,
        "continent": PortAbleResponseTodoslistItemEditedbyCountryContinent,
        "flag": str,
        "name": str,
    },
    total=False,
)

PortAbleResponseTodoslistItemEditedbyCountryItemContinent = TypedDict(
    "PortAbleResponseTodoslistItemEditedbyCountryItemContinent",
    {
        "code": str,
        "name": str,
    },
    total=False,
)

PortAbleResponseTodoslistItemEditedbyCountryItem = TypedDict(
    "PortAbleResponseTodoslistItemEditedbyCountryItem",
    {
        "code": str,
        "continent": PortAbleResponseTodoslistItemEditedbyCountryItemContinent,
        "decimalNotation": int | float,
        "flag": str,
        "name": str,
    },
    total=False,
)

PortAbleResponseTodoslistItemEditedbyCustomfiltersItemFilterslistItem = TypedDict(
    "PortAbleResponseTodoslistItemEditedbyCustomfiltersItemFilterslistItem",
    {
        "comparison": str,
        "field": str,
        "value": List[str],
    },
    total=False,
)

PortAbleResponseTodoslistItemEditedbyCustomfiltersItemOrder = TypedDict(
    "PortAbleResponseTodoslistItemEditedbyCustomfiltersItemOrder",
    {
        "direction": int | float,
        "field": str,
    },
    total=False,
)

PortAbleResponseTodoslistItemEditedbyCustomfiltersItem = TypedDict(
    "PortAbleResponseTodoslistItemEditedbyCustomfiltersItem",
    {
        "filtersList": List[
            PortAbleResponseTodoslistItemEditedbyCustomfiltersItemFilterslistItem
        ],
        "name": str,
        "order": PortAbleResponseTodoslistItemEditedbyCustomfiltersItemOrder,
    },
    total=False,
)

PortAbleResponseTodoslistItemEditedby = TypedDict(
    "PortAbleResponseTodoslistItemEditedby",
    {
        "country": List[PortAbleResponseTodoslistItemEditedbyCountryItem],
        "customFilters": List[PortAbleResponseTodoslistItemEditedbyCustomfiltersItem],
        "email": str,
        "firstname": str,
        "hasNoPdaAccess": bool,
        "id": str,
        "lastname": str,
        "noExcelDownload": None,
        "userRole": int | float,
    },
    total=False,
)

PortAbleResponseTodoslistItem = TypedDict(
    "PortAbleResponseTodoslistItem",
    {
        "editedBy": PortAbleResponseTodoslistItemEditedby,
        "name": str,
        "note": None,
        "order": int | float,
        "status": int | float,
    },
    total=False,
)

PortAbleResponseTrafficmovementslistItemBerthside = TypedDict(
    "PortAbleResponseTrafficmovementslistItemBerthside",
    {
        "name": str,
    },
    total=False,
)

PortAbleResponseTrafficmovementslistItemDraftMetric = TypedDict(
    "PortAbleResponseTrafficmovementslistItemDraftMetric",
    {
        "id": str,
        "name": str,
    },
    total=False,
)

PortAbleResponseTrafficmovementslistItemDraft = TypedDict(
    "PortAbleResponseTrafficmovementslistItemDraft",
    {
        "aft": int | float,
        "fore": int | float,
        "metric": PortAbleResponseTrafficmovementslistItemDraftMetric,
        "mid": int | float,
    },
    total=False,
)

PortAbleResponseTrafficmovementslistItemRoutetoCoords = TypedDict(
    "PortAbleResponseTrafficmovementslistItemRoutetoCoords",
    {
        "lat": int | float,
        "lng": int | float,
    },
    total=False,
)

PortAbleResponseTrafficmovementslistItemRoutetoCountryContinent = TypedDict(
    "PortAbleResponseTrafficmovementslistItemRoutetoCountryContinent",
    {
        "code": str,
        "name": str,
    },
    total=False,
)

PortAbleResponseTrafficmovementslistItemRoutetoCountry = TypedDict(
    "PortAbleResponseTrafficmovementslistItemRoutetoCountry",
    {
        "code": str,
        "continent": PortAbleResponseTrafficmovementslistItemRoutetoCountryContinent,
        "flag": str,
        "name": str,
    },
    total=False,
)

PortAbleResponseTrafficmovementslistItemRouteto = TypedDict(
    "PortAbleResponseTrafficmovementslistItemRouteto",
    {
        "coords": PortAbleResponseTrafficmovementslistItemRoutetoCoords,
        "country": PortAbleResponseTrafficmovementslistItemRoutetoCountry,
        "id": str,
        "isOperational": bool,
        "locode": str,
        "name": str,
        "visiblePortable": bool,
    },
    total=False,
)

PortAbleResponseTrafficmovementslistItemShippingactionslistItemShippingactiontype = TypedDict(
    "PortAbleResponseTrafficmovementslistItemShippingactionslistItemShippingactiontype",
    {
        "actionGroup": int | float,
        "availableTypeList": List[int | float],
        "id": str,
        "label": str,
        "labelActual": str,
        "name": str,
        "order": int | float,
        "requiredTypeList": List[int | float],
    },
    total=False,
)

PortAbleResponseTrafficmovementslistItemShippingactionslistItem = TypedDict(
    "PortAbleResponseTrafficmovementslistItemShippingactionslistItem",
    {
        "date": str,
        "dateLabeled": bool,
        "includeInPortcallSummary": None,
        "isActual": None,
        "remark": None,
        "shippingActionType": PortAbleResponseTrafficmovementslistItemShippingactionslistItemShippingactiontype,
    },
    total=False,
)

PortAbleResponseTrafficmovementslistItemTerminal = TypedDict(
    "PortAbleResponseTrafficmovementslistItemTerminal",
    {
        "id": str,
        "name": str,
        "restriction": str,
        "restrictionsList": str,
        "type": int | float,
    },
    total=False,
)

PortAbleResponseTrafficmovementslistItem = TypedDict(
    "PortAbleResponseTrafficmovementslistItem",
    {
        "berthSide": PortAbleResponseTrafficmovementslistItemBerthside,
        "draft": PortAbleResponseTrafficmovementslistItemDraft,
        "name": str,
        "remark": None,
        "routeTo": PortAbleResponseTrafficmovementslistItemRouteto,
        "shippingActionsList": List[
            PortAbleResponseTrafficmovementslistItemShippingactionslistItem
        ],
        "terminal": PortAbleResponseTrafficmovementslistItemTerminal,
        "type": int | float,
    },
    total=False,
)

PortAbleResponseUpdatedbyCountryItemContinent = TypedDict(
    "PortAbleResponseUpdatedbyCountryItemContinent",
    {
        "code": str,
        "name": str,
    },
    total=False,
)

PortAbleResponseUpdatedbyCountryItem = TypedDict(
    "PortAbleResponseUpdatedbyCountryItem",
    {
        "code": str,
        "continent": PortAbleResponseUpdatedbyCountryItemContinent,
        "decimalNotation": None,
        "flag": str,
        "name": str,
    },
    total=False,
)

PortAbleResponseUpdatedbyCustomfiltersItemFilterslistItem = TypedDict(
    "PortAbleResponseUpdatedbyCustomfiltersItemFilterslistItem",
    {
        "comparison": str,
        "field": str,
        "value": List[str],
    },
    total=False,
)

PortAbleResponseUpdatedbyCustomfiltersItemOrder = TypedDict(
    "PortAbleResponseUpdatedbyCustomfiltersItemOrder",
    {
        "direction": int | float,
        "field": str,
    },
    total=False,
)

PortAbleResponseUpdatedbyCustomfiltersItem = TypedDict(
    "PortAbleResponseUpdatedbyCustomfiltersItem",
    {
        "filtersList": List[PortAbleResponseUpdatedbyCustomfiltersItemFilterslistItem],
        "name": str,
        "order": PortAbleResponseUpdatedbyCustomfiltersItemOrder,
    },
    total=False,
)

PortAbleResponseUpdatedby = TypedDict(
    "PortAbleResponseUpdatedby",
    {
        "country": List[PortAbleResponseUpdatedbyCountryItem],
        "customFilters": List[PortAbleResponseUpdatedbyCustomfiltersItem],
        "email": str,
        "firstname": str,
        "hasNoPdaAccess": bool,
        "id": str,
        "lastname": str,
        "noExcelDownload": bool,
        "userRole": int | float,
    },
    total=False,
)

PortAbleResponseVessel = TypedDict(
    "PortAbleResponseVessel",
    {
        "id": str,
        "imo": str,
        "name": Required[str],
        "photo": str,
    },
    total=False,
)

PortAbleResponse = TypedDict(
    "PortAbleResponse",
    {
        "activeTM": int | float,
        "agencyFeesList": str,
        "attachmentsList": Required[List[PortAbleResponseAttachmentslistItem]],
        "bunkersList": List[PortAbleResponseBunkerslistItem],
        "cargosList": List[PortAbleResponseCargoslistItem],
        "createdAt": str,
        "currentForm": int | float,
        "daOwner": Required[PortAbleResponseDaowner],
        "emailOptions": List[PortAbleResponseEmailoptionsItem],
        "hasFinancialProject": bool,
        "husbandry": Required[PortAbleResponseHusbandry],
        "id": str,
        "isFavourite": bool,
        "isInvoiceThrough": bool,
        "isNomination": bool,
        "nor": PortAbleResponseNor,
        "notesList": List[PortAbleResponseNoteslistItem],
        "otherPartiesList": Required[List[PortAbleResponseOtherpartieslistItem]],
        "pdaStatus": PortAbleResponsePdastatus,
        "portOfCall": PortAbleResponsePortofcall,
        "portablePartiesList": Required[List[PortAbleResponsePortablepartieslistItem]],
        "portcallResponsibles": List[PortAbleResponsePortcallresponsiblesItem],
        "principal": Required[PortAbleResponsePrincipal],
        "purposeCall": PortAbleResponsePurposecall,
        "recipientsList": List[PortAbleResponseRecipientslistItem],
        "remarksList": List[PortAbleResponseRemarkslistItem],
        "sofSettings": PortAbleResponseSofsettings,
        "status": PortAbleResponseStatus,
        "stoppageActionsList": str,
        "stowagePlan": PortAbleResponseStowageplan,
        "subStatus": PortAbleResponseSubstatus,
        "todosList": List[PortAbleResponseTodoslistItem],
        "trafficMovementsList": List[PortAbleResponseTrafficmovementslistItem],
        "uniqueNumber": str,
        "updatedAt": str,
        "updatedBy": PortAbleResponseUpdatedby,
        "vessel": Required[PortAbleResponseVessel],
    },
    total=False,
)


PascalResponseHitCounts = TypedDict(
    "PascalResponseHitCounts",
    {
        "enforcements": int,
        "news": int,
        "other": int,
        "peps": int,
        "sanctions": Required[int],
    },
    total=False,
)

PascalResponseHitCounts = TypedDict(
    "PascalResponseHitCounts",
    {
        "negative": PascalResponseHitCounts,
        "positive": PascalResponseHitCounts,
        "unresolved": PascalResponseHitCounts,
    },
    total=True,
)

PascalResponseSourcesItemDataSource = TypedDict(
    "PascalResponseSourcesItemDataSource",
    {
        "active": bool,
        "deactivated_at": None,
        "id": int,
        "source": str,
        "vendor": str,
    },
    total=False,
)

PascalResponseSourcesItem = TypedDict(
    "PascalResponseSourcesItem",
    {
        "active": bool,
        "case_id": int,
        "data_source": PascalResponseSourcesItemDataSource,
        "data_source_id": int,
        "id": int,
        "searched_at": str,
        "succeeded": bool,
    },
    total=False,
)

PascalResponse = TypedDict(
    "PascalResponse",
    {
        "additional_terms": None,
        "addresses": None,
        "aliases": None,
        "all_sources_searched": bool,
        "asset_type": None,
        "clients": str,
        "company_number": None,
        "confidence": str,
        "country": str,
        "country_of_birth": None,
        "country_of_residence": None,
        "created_at": str,
        "date_of_birth": None,
        "deleted_at": None,
        "description": None,
        "excluded_terms": None,
        "external_identifier": None,
        "gender": None,
        "group_id": None,
        "hit_counts": Required[PascalResponseHitCounts],
        "hubspot_portal_id": None,
        "id": int,
        "identifier": None,
        "match_on_connections": bool,
        "monitoring_frequency_enforcements": int,
        "monitoring_frequency_news": int,
        "monitoring_frequency_other": int,
        "monitoring_frequency_peps": int,
        "monitoring_frequency_sanctions": int,
        "name": str,
        "nationalities": None,
        "organization_id": int,
        "origin": str,
        "risk": None,
        "salesforce_object_id": None,
        "searched_at": str,
        "services": List[str],
        "sources": List[PascalResponseSourcesItem],
        "status": Required[str],
        "type": str,
        "unresolved_risk": None,
        "updated_at": str,
        "user_id": int,
        "uuid": Required[str],
    },
    total=False,
)
