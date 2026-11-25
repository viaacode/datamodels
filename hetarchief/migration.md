# Migration legacy ontologies to the new hetarchief model

Prepared from the workspace sources on 24 November 2026.

Most used terms have a clear destination in the consolidated `ha:` namespace, while PREMIS, PROV and ODRL terms largely retain their external IRIs. A complete migration cannot be implemented as a namespace replacement: several properties change their value structure or meaning, and some target declarations conflict with the source shapes. The tables below distinguish direct mappings, required transformations and unresolved decisions.

## Scope and evidence

The inventory starts with active `sh:targetClass`, `sh:class` and `sh:path` statements in the source shapes, including nested `sh:or` alternatives and reusable property shapes. It also includes the resource IRIs in `sh:in` lists, because those values must migrate with their properties. Comments, unused prefix declarations, SHACL machinery and ontology-document metadata are excluded. A term occurring in several files has one crosswalk entry. Datatypes retain their IRIs unless a specific conversion is identified below.

| Code | Source shape file | Distinct classes used | Distinct properties used |
| --- | --- | ---: | ---: |
| D | `description/description.shacl.ttl` | 49 | 105 |
| E | `events/events.shacl.ttl` | 9 | 18 |
| O | `objects/objects.shacl.ttl` | 16 | 50 |
| G | `organizations/organizations.shacl.ttl` | 18 | 42 |
| R | `rights/rights.shacl.ttl` | 16 | 17 |

The five source files contain **90 distinct classes and 211 distinct properties**. Counts overlap between source files and must not be summed.

Destinations were checked against `hetarchief/model.rdfs.ttl` and its three imported extracts: `hetarchief/external/premis.rdfs.ttl`, `hetarchief/external/prov.rdfs.ttl` and `hetarchief/external/odrl.rdfs.ttl`. Legacy RDFS definitions in the five source directories and `ontologies/` clarify meaning where necessary; selected local SKOS files clarify enumerated values. Terms defined only in legacy RDFS, but never used by the source shapes, are outside this crosswalk. In particular, no `haEvt:` classes or properties occur in the event shapes.

**`hetarchief/model.shacl.ttl` was not used.** No target validation rules are inferred from that unfinished file. This is a schema-based migration plan; no production instance data was supplied or profiled.

An explicit `owl:equivalentClass` or `owl:equivalentProperty` is stronger evidence than `rdfs:seeAlso`. The latter helps identify a candidate but does not assert equivalence. Local renames were checked against definitions and comments. RDFS domain/range statements imply types; they are not validation constraints. Conflicting declarations below therefore identify both semantic risks and decisions needed before a migration validation profile can be written.

## Status legend

| Status | Meaning and migration action |
| --- | --- |
| MAP | Destination is sufficiently clear for a direct term replacement in the stated context. Preserve subject/object direction and literal values. |
| KEEP | Keep the same IRI. External or foundational vocabulary remains in use; linked classes and controlled values can still change. |
| CHANGE | Destination is clear, but apply the stated structural or value transformation. |
| REVIEW | **Uncertain mapping, unresolved conversion, or target-model conflict.** The stated destination is a candidate, not an instruction to transform blindly. |
| UNMAPPED | **No adequate supported destination identified.** Retain the original statement in a legacy/provenance graph until a decision is recorded. |

`M01`–`M17` refer to the decisions and transformation rules after the crosswalk. A MAP or KEEP row does not override a linked issue or the cross-cutting checks in the execution plan.

## Namespace key

Prefixes identify exact IRIs; spelling, case, `http`/`https` and trailing separators matter.

| Prefix | Namespace |
| --- | --- |
| `ha` | `https://data.hetarchief.be/ns/` |
| `haDes` | `https://data.hetarchief.be/ns/description/` |
| `haObj` | `https://data.hetarchief.be/ns/object/` |
| `haOrg` | `https://data.hetarchief.be/ns/organization/` |
| `haRig` | `https://data.hetarchief.be/ns/rights/` |
| `mh` | `https://data.hetarchief.be/ns/mediahaven/` |
| `schema` | `https://schema.org/` |
| `premis` | `http://www.loc.gov/premis/rdf/v3/` |
| `prov` | `http://www.w3.org/ns/prov#` |
| `odrl` | `http://www.w3.org/ns/odrl/2/` |
| `org` | `http://www.w3.org/ns/org#` |
| `dct` | `http://purl.org/dc/terms/` |
| `ebucore` | `http://www.ebu.ch/metadata/ontologies/ebucore/ebucore#` |
| `edm` | `http://www.europeana.eu/schemas/edm/` |
| `bf` | `http://id.loc.gov/ontologies/bibframe/` |
| `foaf` | `http://xmlns.com/foaf/0.1/` |
| `rel` | `http://id.loc.gov/vocabulary/preservation/relationshipSubType/` |
| `evtAgRole` | `http://id.loc.gov/vocabulary/preservation/eventRelatedAgentRole/` |
| `evtObjRole` | `http://id.loc.gov/vocabulary/preservation/eventRelatedObjectRole/` |
| `evtOutcome` | `http://id.loc.gov/vocabulary/preservation/eventOutcome/` |
| `copyrightStatus` | `http://id.loc.gov/vocabulary/preservation/copyrightStatus/` |
| `skos` | `http://www.w3.org/2004/02/skos/core#` |
| `rdf` | `http://www.w3.org/1999/02/22-rdf-syntax-ns#` |
| `xsd` | `http://www.w3.org/2001/XMLSchema#` |
| `edtf` | `http://id.loc.gov/datatypes/edtf/` |

## Class crosswalk

These rows cover both shape targets and classes allowed as property values. Replace class IRIs in `rdf:type` assertions and relevant class references; this does not authorize changing resource instance IRIs.

### Legacy description classes

| Source term | Target term / action | Status | Used in | Notes |
| --- | --- | --- | --- | --- |
| `haDes:2DArtwork` | `ha:TwoDimensionalArtwork` | **MAP** | D | — |
| `haDes:3DArtwork` | `ha:ThreeDimensionalArtwork` | **MAP** | D | — |
| `haDes:Audio` | `ha:Audio` | **MAP** | D | — |
| `haDes:AudioReel` | `ha:SoundReel` | **MAP** | D | Explicit rename in the target comment. |
| `haDes:AudiovisualCarrier` | `ha:AudiovisualCarrier` | **MAP** | D | — |
| `haDes:AudiovisualCarrierRepresentation` | `ha:AudiovisualCarrierRepresentation` | **MAP** | D | — |
| `haDes:DVD` | `ha:DVD` | **MAP** | D | — |
| `haDes:DVDChapter` | `ha:DVDChapter` | **MAP** | D | — |
| `haDes:Film` | `ha:Film` | **MAP** | D | — |
| `haDes:FilmCarrierRepresentation` | `ha:FilmCarrierRepresentation` | **MAP** | D | — |
| `haDes:Image` | `ha:Image` | **MAP** | D | — |
| `haDes:ImageReel` | `ha:ImageReel` | **MAP** | D | — |
| `haDes:MaterialArtwork` | `ha:MaterialArtwork` | **MAP** | D | — |
| `haDes:NewspaperIssue` | `ha:NewspaperIssue` | **MAP** | D | — |
| `haDes:NewspaperIssuePage` | `ha:NewspaperIssuePage` | **MAP** | D | — |
| `haDes:RoleName` | `ha:RoleType` | **MAP** | D | Controlled role concept; M02. |
| `haDes:SilentFilm` | `ha:SilentFilm` | **MAP** | D | — |
| `haDes:SoundFilm` | `ha:SoundFilm` | **MAP** | D | — |
| `haDes:Video` | `ha:Video` | **MAP** | D | — |
| `haDes:WrittenWorkCarrierRepresentation` | `ha:WrittenWorkCarrierRepresentation` | **MAP** | D | — |

### Legacy object classes

| Source term | Target term / action | Status | Used in | Notes |
| --- | --- | --- | --- | --- |
| `haObj:CarrierRepresentation` | `ha:CarrierRepresentation` | **MAP** | D, O | — |
| `haObj:DigitalRepresentation` | `ha:DigitalRepresentation` | **MAP** | D, O, R | — |
| `haObj:FragmentRepresentation` | `ha:FragmentRepresentation` | **REVIEW** | O | Target equates this with ha:MediaFragment; M04. |
| `haObj:LocalIdentifier` | `ha:LocalIdentifier` | **MAP** | O | — |
| `haObj:PhysicalCarrier` | `ha:PhysicalCarrier` | **MAP** | D, O | — |
| `mh:Fragment` | `ha:MediahavenFragment` | **MAP** | O | — |
| `mh:Record` | `ha:MediahavenRecord` | **MAP** | O | — |

### Legacy organization and rights classes

| Source term | Target term / action | Status | Used in | Notes |
| --- | --- | --- | --- | --- |
| `haOrg:ContentPartner` | `ha:ContentPartner` | **MAP** | D, G | — |
| `haOrg:DigitizationPartner` | `ha:DigitizationPartner` | **MAP** | G | — |
| `haOrg:EducationalPartner` | `ha:EducationalPartner` | **MAP** | G | — |
| `haOrg:Logo` | `ha:Logo` | **MAP** | G | — |
| `haOrg:OrganizationType` | `ha:OrganizationType` | **MAP** | G | — |
| `haOrg:ProjectPartner` | `ha:ProjectPartner` | **MAP** | G | — |
| `haOrg:ServiceConsumer` | `ha:ServiceConsumer` | **MAP** | G | — |
| `haOrg:ServiceProvider` | `ha:ServiceProvider` | **MAP** | G | — |
| `haRig:ContentRange` | `ha:ContentScope` | **MAP** | R | — |
| `haRig:MetadataRange` | `ha:MetadataScope` | **MAP** | R | - |
| `haRig:Motivation` | `ha:Motivation` | **MAP** | R | — |
| `haRig:UserGroup` | `ha:UserGroup` | **MAP** | R | — |

### External descriptive and organization classes

| Source term | Target term / action | Status | Used in | Notes |
| --- | --- | --- | --- | --- |
| `copyrightStatus:pub` | `ha:PublicDomainStatus` | **MAP** | R | - |
| `dct:FileFormat` | `ha:FileFormat` | **MAP** | O | — |
| `dct:RightsStatement` | `ha:RightsStatement` | **MAP** | R | — |
| `ebucore:Annotation` | `ha:Annotation` | **MAP** | D | — |
| `ebucore:ClosedCaptions` | `ha:ClosedSubtitling` | **MAP** | D | Accessibility captions and general subtitles must be distinguished; M08. |
| `ebucore:MediaFragment` | `ha:MediaFragment` | **REVIEW** | D | Candidate is clear; target hierarchy and equivalence need a decision; M04. |
| `ebucore:OpenCaptions` | `ha:OpenSubtitling` | **MAP** | D | Accessibility captions and general subtitles must be distinguished; M08. |
| `ebucore:TextAnnotation` | `ha:TextAnnotation` | **MAP** | D | — |
| `org:Organization` | `ha:Organization` | **MAP** | D, E, G | — |
| `org:OrganizationalUnit` | `ha:OrganizationalUnit` | **MAP** | G | — |
| `org:Post` | `ha:Post` | **MAP** | G | — |
| `org:Role` | `ha:RoleType` | **MAP** | G | - |
| `org:Site` | `ha:Site` | **MAP** | G | — |
| `schema:ArchiveComponent` | `ha:ArchiveComponent` | **MAP** | D | — |
| `schema:Brand` | `ha:Brand` | **MAP** | D, E | — |
| `schema:BroadcastEvent` | `ha:BroadcastEvent` | **MAP** | D | — |
| `schema:Collection` | `ha:Collection` | **MAP** | D | — |
| `schema:ContactPoint` | `ha:ContactPoint` | **MAP** | G | — |
| `schema:Country` | `ha:Country` | **MAP** | G | — |
| `schema:CreativeWork` | `premis:IntellectualEntity` (per resource) | **MAP** | D | - |
| `schema:CreativeWorkSeason` | `ha:Season` | **MAP** | D | — |
| `schema:CreativeWorkSeries` | `ha:Series` | **MAP** | D | — |
| `schema:Episode` | `ha:Episode` | **MAP** | D | — |
| `schema:Newspaper` | `ha:Newspaper` | **MAP** | D | — |
| `schema:PerformanceRole` | `ha:PerformanceRole` | **MAP** | D | - |
| `schema:Person` | `ha:Person` | **MAP** | D, E, G | — |
| `schema:Place` | `ha:Place` | **MAP** | D | — |
| `schema:PostalAddress` | `ha:PostalAddress` | **MAP** | G | — |
| `schema:QuantitativeValue` | `ha:QuantitativeValue` | **MAP** | D, O | — |
| `schema:Role` | `ha:Role` | **CHANGE** | D | Preserve role identity and move its agent link to rdf:value; M02. |
| `schema:Thing` | `ha:Thing` | **MAP** | D | — |
| `skos:Concept` | `skos:Concept` | **KEEP** | D, G, R | Used by the target model; preserve concept identities and SKOS descriptions. |

### External classes retained through imports

| Source term | Target term / action | Status | Used in | Notes |
| --- | --- | --- | --- | --- |
| `odrl:Action` | `odrl:Action` | **KEEP** | R | Retained in the imported external ontology. |
| `odrl:Constraint` | `odrl:Constraint` | **KEEP** | R | Retained in the imported external ontology. |
| `odrl:Permission` | `odrl:Permission` | **KEEP** | R | Retained in the imported external ontology. |
| `odrl:Policy` | `odrl:Policy` | **KEEP** | R | Retained in the imported external ontology. |
| `odrl:Prohibition` | `odrl:Prohibition` | **KEEP** | R | Retained in the imported external ontology. |
| `premis:Event` | `premis:Event` | **KEEP** | E | Retained in the imported external ontology. |
| `premis:File` | `premis:File` | **KEEP** | D, O | Retained in the imported external ontology. |
| `premis:Fixity` | `premis:Fixity` | **KEEP** | O | Retained in the imported external ontology. |
| `premis:HardwareAgent` | `premis:HardwareAgent` | **KEEP** | E | Retained in the imported external ontology. |
| `premis:IntellectualEntity` | `premis:IntellectualEntity` | **KEEP** | D, O, R | Retained in the imported external ontology. |
| `premis:License` | `premis:License` | **KEEP** | R | Retained in the imported external ontology. |
| `premis:Object` | `premis:Object` | **KEEP** | E, O | Retained in the imported external ontology. |
| `premis:OutcomeStatus` | `premis:OutcomeStatus` | **KEEP** | E | Retained in the imported external ontology. |
| `premis:Representation` | `premis:Representation` | **KEEP** | D, O | Retained in the imported external ontology. |
| `premis:RightsStatus` | `premis:RightsStatus` | **KEEP** | R | Retained in the imported external ontology. |
| `premis:SoftwareAgent` | `premis:SoftwareAgent` | **KEEP** | E | Retained in the imported external ontology. |
| `premis:StorageLocation` | `premis:StorageLocation` | **KEEP** | O | Retained in the imported external ontology. |
| `premis:StorageMedium` | `premis:StorageMedium` | **KEEP** | O | Retained in the imported external ontology. |
| `prov:Activity` | `prov:Activity` | **KEEP** | E | Retained in the imported external ontology. |

## Property crosswalk

Apply mappings by subject type and graph context. In particular, the same contribution property on a work and on a role wrapper has different migration actions. The source-file column identifies every shape file where the predicate occurs.

### Legacy description properties

| Source term | Target term / action | Status | Used in | Notes |
| --- | --- | --- | --- | --- |
| `haDes:aspectRatio` | `ha:hasAspectRatio` | **MAP** | D | — |
| `haDes:audioNoiseReduction` | `ha:hasAudioNoiseReduction` | **MAP** | D | — |
| `haDes:audioRecordingSpeed` | `ha:hasAudioRecordingSpeed` | **REVIEW** | D | Measurement links mostly fit; variable-speed concept has no numeric value; M05. |
| `haDes:broadcastingOrganization` | `ha:hasBroadcastingOrganization` | **MAP** | D | — |
| `haDes:chapterNumber` | `ha:hasChapterNumber` | **MAP** | D | — |
| `haDes:coloringType` | `ha:hasFilmColorType` | **MAP** | D | — |
| `haDes:executor` | `ha:hasExecutor` | **CHANGE** | D | On a work, rename; on a role, move the agent link to rdf:value; M02. |
| `haDes:hasMissingAudioReels` | `ha:hasMissingSoundReels` | **MAP** | D | — |
| `haDes:hasMissingImageReels` | `ha:hasMissingImageReels` | **MAP** | D | — |
| `haDes:iec60094Type` | `ha:hasIEC60094Type` | **MAP** | D | — |
| `haDes:licenseDistributor` | `ha:hasLicenseDistributor` | **MAP** | D | - |
| `haDes:numberOfAudioChannels` | `ha:hasNumberOfAudioChannels` | **MAP** | D | — |
| `haDes:numberOfAudioTracks` | `ha:hasNumberOfAudioTracks` | **MAP** | D | — |
| `haDes:numberOfMissingAudioReels` | `ha:hasNumberOfMissingSoundReels` | **MAP** | D | — |
| `haDes:numberOfMissingImageReels` | `ha:hasNumberOfMissingImageReels` | **MAP** | D | — |
| `haDes:numberOfPages` | `ha:hasNumberOfPages` | **MAP** | D | — |
| `haDes:numberOfReels` | `ha:hasNumberOfReels` | **MAP** | D | — |
| `haDes:owner` | `ha:hasOwner` | **MAP** | D | — |
| `haDes:pageNumber` | `ha:hasPageNumber` | **MAP** | D | — |

### Legacy object and Mediahaven properties

| Source term | Target term / action | Status | Used in | Notes |
| --- | --- | --- | --- | --- |
| `haObj:hasAccessCopy` | `ha:hasAccessCopy` | **MAP** | O | — |
| `haObj:hasCarrierCopy` | `ha:hasCarrierRepresentation` | **MAP** | D, O | — |
| `haObj:hasFragmentRepresentation` | `ha:hasFragmentRepresentation` | **MAP** | O | — |
| `haObj:hasIIIFCopy` | `ha:hasIIIFCopy` | **MAP** | O | — |
| `haObj:hasMasterCopy` | `ha:hasMasterCopy` | **MAP** | O | — |
| `haObj:hasMezzanineCopy` | `ha:hasMezzanineCopy` | **MAP** | O | — |
| `haObj:hasTranscriptionCopy` | `ha:hasTranscriptionCopy` | **MAP** | O | — |
| `haObj:isAccessCopyOf` | `ha:isAccessCopyOf` | **MAP** | O | Preserve representation-to-intellectual-entity direction; current target domain/range agree; M16. |
| `haObj:isCarrierCopyOf` | `ha:isCarrierRepresentationOf` | **MAP** | O | — |
| `haObj:isFragmentRepresentationOf` | `ha:isFragmentRepresentationOf` | **MAP** | O | — |
| `haObj:isIIIFCopyOf` | `ha:isIIIFCopyOf` | **MAP** | O | — |
| `haObj:isMasterCopyOf` | `ha:isMasterCopyOf` | **MAP** | O | — |
| `haObj:isMezzanineCopyOf` | `ha:isMezzanineCopyOf` | **MAP** | O | — |
| `haObj:isTranscriptionCopyOf` | `ha:isTranscriptionCopyOf` | **MAP** | O | — |
| `haObj:preservationProblem` | `ha:hasPreservationProblem` | **MAP** | D | — |
| `haObj:primaryIdentifier` | `ha:hasPrimaryLocalIdentifier` | **MAP** | O | Primary identifier node stays distinct from generic identifier links; M01. |
| `mh:record` | `ha:hasRecord` | **MAP** | O | — |
| `mh:tenantName` | `ha:hasTenantName` | **MAP** | G | — |

### Legacy organization and rights properties

| Source term | Target term / action | Status | Used in | Notes |
| --- | --- | --- | --- | --- |
| `haOrg:hasAccountManager` | `ha:hasAccountManager` | **MAP** | G | — |
| `haOrg:hasLogo` | `ha:hasLogo` | **MAP** | G | — |
| `haOrg:hasPreference` | `ha:hasPreference` | **MAP** | G | — |
| `haOrg:isAccountManagerOf` | `ha:isAccountManagerOf` | **MAP** | G | — |
| `haOrg:requestForm` | `ha:hasContentRequestFormTemplate` | **MAP** | G | - |
| `haOrg:sector` | `ha:hasSector` | **MAP** | G | — |
| `haRig:isMotivatedBy` | `ha:isMotivatedBy` | **MAP** | R | — |

### External organization properties

| Source term | Target term / action | Status | Used in | Notes |
| --- | --- | --- | --- | --- |
| `org:classification` | `ha:hasClassification` | **MAP** | G | — |
| `org:hasPost` | `ha:hasPost` | **MAP** | G | — |
| `org:hasPrimarySite` | `ha:hasPrimarySite` | **MAP** | G | — |
| `org:hasSite` | `ha:hasSite` | **MAP** | G | — |
| `org:hasUnit` | `ha:hasUnit` | **MAP** | G | — |
| `org:holds` | `ha:holds` | **MAP** | G | — |
| `org:identifier` | `ha:hasIdentifier` | **REVIEW** | G | Source literal versus target identifier node and datatype-property declaration; M01. |
| `org:postIn` | `ha:isPostIn` | **MAP** | G | — |
| `org:role` | `ha:hasRoleType` | **REVIEW** | G | Post to abstract role type; class choice and Post hierarchy need resolution; M02. |
| `org:siteAddress` | `ha:hasSiteAddress` | **MAP** | G | — |
| `org:siteOf` | `ha:isSiteOf` | **MAP** | G | — |
| `org:unitOf` | `ha:isUnitOf` | **MAP** | G | — |

### Schema.org properties

| Source term | Target term / action | Status | Used in | Notes |
| --- | --- | --- | --- | --- |
| `schema:about` | `ha:isAbout` | **MAP** | D | — |
| `schema:abstract` | `ha:hasAbstract` | **REVIEW** | D | Source language-tagged literal versus xsd:string; superproperty also disagrees; M07. |
| `schema:actor` | `ha:hasActor` | **REVIEW** | D | Work-to-performance-role and role-to-agent usages require separate handling; M02. |
| `schema:addressCountry` | `ha:hasAddressCountry` | **REVIEW** | G | Preserve country nodes; resolve literal countries to entities; M12. |
| `schema:addressLocality` | `ha:hasAddressLocality` | **MAP** | G | — |
| `schema:addressRegion` | `ha:hasAddressRegion` | **MAP** | G | — |
| `schema:alternateName` | `ha:hasAlternateName` | **REVIEW** | D | Source language tags conflict with target xsd:string; M07. |
| `schema:artMedium` | `ha:hasArtMedium` | **REVIEW** | D | Source language tags conflict with target xsd:string; M07. |
| `schema:artform` | `ha:hasArtform` | **REVIEW** | D | Source language tags conflict with target xsd:string; M07. |
| `schema:birthDate` | `ha:hasBirthDate` | **MAP** | G | — |
| `schema:birthPlace` | `ha:hasBirthPlace` | **REVIEW** | G | Source literal versus entity; target still ranges over schema:Place; M12. |
| `schema:brand` | `ha:hasBrand` | **MAP** | D, E | — |
| `schema:caption` | `ha:hasCaptionText` | **REVIEW** | D | Target domain is undefined ha:File; source uses a digital representation; M08. |
| `schema:characterName` | `ha:hasCharacterName` | **MAP** | D | — |
| `schema:collectionSize` | `ha:hasCollectionSize` | **CHANGE** | D | Require nonnegative values; retype valid integers to xsd:nonNegativeInteger. |
| `schema:contactPoint` | `ha:hasContactPoint` | **MAP** | G | — |
| `schema:contactType` | `ha:hasContactType` | **MAP** | G | — |
| `schema:containedInPlace` | `ha:isContainedInPlace` | **MAP** | D | — |
| `schema:contributor` | `ha:hasContributor` | **CHANGE** | D | On a work, rename; on a role, move the agent link to rdf:value; M02. |
| `schema:copyrightHolder` | `ha:hasRightsHolder` | **REVIEW** | D | Target ha:Agent excludes unidentified generic things unless classified; M02. |
| `schema:copyrightNotice` | No exact target (`ha:hasRights` is a broader candidate) | **UNMAPPED** | D | No dedicated notice predicate; broader rights text would lose the distinction; M14. |
| `schema:copyrightYear` | `ha:hasCopyrightDate` | **REVIEW** | D | Year-only integer cannot become a precise xsd:dateTime without inventing information; M06. |
| `schema:creator` | `ha:hasCreator` | **REVIEW** | D, O | Work-to-role: rename; role-to-agent: rdf:value. Fixity string usage has no safe direct mapping; M02/M13. |
| `schema:creditText` | `ha:hasCreditText` | **REVIEW** | D | Source language tags conflict with target xsd:string; M07. |
| `schema:dateCreated` | `ha:hasCreationDate` | **REVIEW** | D, O | EDTF to dateTime plus source File/MediahavenFragment domain gaps; M06. |
| `schema:dateDeleted` | `ha:hasDeletionDate` | **MAP** | O | Mediahaven fragment deletion timestamp; preserve xsd:dateTime. |
| `schema:dateModified` | `ha:hasModificationDate` | **MAP** | O | Mediahaven fragment modification timestamp; preserve xsd:dateTime. |
| `schema:datePublished` | `ha:hasPublicationDate` | **REVIEW** | D | EDTF levels 0/2 and digital-representation subjects need a policy; M06. |
| `schema:deathDate` | `ha:hasDeathDate` | **MAP** | G | — |
| `schema:deathPlace` | `ha:hasDeathPlace` | **REVIEW** | G | Source literal must become a resolved place entity; M12. |
| `schema:depth` | `ha:hasDepth` | **MAP** | D | — |
| `schema:description` | `ha:hasDescription` | **MAP** | D | — |
| `schema:duration` | `ha:hasDuration` | **MAP** | D, O | — |
| `schema:email` | `ha:hasEmail` | **MAP** | G | — |
| `schema:endDate` | `ha:hasEndDate` | **MAP** | D | — |
| `schema:endTime` | `ha:hasEndOffset` | **REVIEW** | D, O | xsd:time to integer seconds relative to media start; M04. |
| `schema:familyName` | `ha:hasFamilyName` | **MAP** | G | — |
| `schema:genre` | `ha:hasGenre` | **REVIEW** | D | Source language tags conflict with target xsd:string; M07. |
| `schema:givenName` | `ha:hasGivenName` | **MAP** | G | — |
| `schema:hasPart` | `ha:hasPart` | **MAP** | D | — |
| `schema:height` | `ha:hasHeight` | **REVIEW** | D, O | Keep measurement nodes; file subjects omitted from target domain; unionOF typo; M05. |
| `schema:identifier` | `ha:hasIdentifier` | **REVIEW** | D, O | Source literal versus target identifier node and datatype-property declaration; M01. |
| `schema:inLanguage` | `ha:hasLanguage` | **REVIEW** | D | Validate/normalize xsd:language; representation/caption subjects exceed domain; M07. |
| `schema:instrument` | `ha:hasInstrument` | **MAP** | E | — |
| `schema:isPartOf` | `ha:isPartOf` | **REVIEW** | D | Most individual-to-collection links fit; source also uses collection subjects; M10. |
| `schema:issueNumber` | `ha:hasIssueNumber` | **REVIEW** | D | Source permits strings; target superproperty ha:hasPosition has an integer range; M10. |
| `schema:keywords` | `ha:hasKeywords` | **REVIEW** | D | Source language tags conflict with target xsd:string; M07. |
| `schema:license` | `ha:hasLicense` | **MAP** | D | — |
| `schema:locationCreated` | `ha:hasCreationPlace` | **REVIEW** | D | Source uses a newspaper series; target domain is an intellectual entity; M10/M12. |
| `schema:logo` | `ha:hasLogo` | **MAP** | G | — |
| `schema:maintainer` | `ha:hasMaintainer` | **MAP** | D | — |
| `schema:material` | `ha:hasMaterial` | **MAP** | D | — |
| `schema:materialExtent` | `ha:hasMaterialExtent` | **MAP** | D | — |
| `schema:mentions` | `ha:mentions` | **MAP** | D | — |
| `schema:model` | `ha:hasModel` | **MAP** | E | — |
| `schema:name` | `ha:hasName` | **REVIEW** | D, E, G | Most source names are language-tagged; target expects xsd:string; M07. |
| `schema:position` | `ha:hasPosition` | **REVIEW** | D | Source uses a series subject, but target domain is an intellectual entity; M10. |
| `schema:postOfficeBoxNumber` | `ha:hasPostOfficeBoxNumber` | **MAP** | G | — |
| `schema:postalCode` | `ha:hasPostalCode` | **MAP** | G | — |
| `schema:producer` | `ha:hasProducer` | **REVIEW** | D | Work-to-role fits; role-to-agent must use rdf:value; M02. |
| `schema:publisher` | `ha:hasPublisher` | **CHANGE** | D | On a work, rename; on a role, move the agent link to rdf:value; M02. |
| `schema:roleName` | `ha:hasRoleType` | **REVIEW** | D | Concepts can be retyped; free-text names need controlled role concepts; M02. |
| `schema:seasonNumber` | `ha:hasSeasonNumber` | **REVIEW** | D | Season link fits; integer-valued parent ha:hasPosition adds an intellectual-entity domain; M10. |
| `schema:serialNumber` | `ha:hasSerialNumber` | **REVIEW** | E | String value inherits the unresolved identifier-node range; M01. |
| `schema:spatial` | `ha:hasSpatial` | **REVIEW** | D | Place link fits directly, but target superproperty ha:hasCoverage has a string range; M12. |
| `schema:startDate` | `ha:hasStartDate` | **MAP** | D | — |
| `schema:startTime` | `ha:hasStartOffset` | **REVIEW** | D, O | xsd:time to integer seconds relative to media start; M04. |
| `schema:streetAddress` | `ha:hasStreetAddress` | **MAP** | G | — |
| `schema:telephone` | `ha:hasTelephone` | **MAP** | G | — |
| `schema:temporal` | `ha:hasTemporal` | **REVIEW** | D | Source language tags conflict with target xsd:string; M07. |
| `schema:thumbnailUrl` | `ha:hasThumbnailURL` | **CHANGE** | D | Source IRI becomes an xsd:anyURI literal if following the declared range; M07. |
| `schema:transcript` | `ha:hasTranscript` | **REVIEW** | D | Source subject is a digital representation; target domain is an intellectual entity; M08. |
| `schema:unitCode` | `ha:hasUnitCode` | **MAP** | D | — |
| `schema:unitText` | `ha:hasUnitText` | **MAP** | D | — |
| `schema:value` | `ha:hasMeasurementValue` | **MAP** | D | Only quantitative measurements map here; keep xsd:float; M05. |
| `schema:vatID` | `ha:hasVATID` | **MAP** | G | — |
| `schema:version` | `ha:hasVersion` | **MAP** | E | — |
| `schema:width` | `ha:hasWidth` | **REVIEW** | D, O | Keep measurement nodes; file subjects omitted from target domain; M05. |

### Dublin Core, BIBFRAME and FOAF properties

| Source term | Target term / action | Status | Used in | Notes |
| --- | --- | --- | --- | --- |
| `bf:edition` | `ha:hasEdition` | **REVIEW** | D | Concept object is preserved, but target declares owl:DatatypeProperty; M11. |
| `bf:issuance` | `ha:hasIssuance` | **REVIEW** | D | Source means frequency; target means mode of issuance; M11. |
| `bf:precededBy` | `ha:isPrecededBy` | **REVIEW** | D | Source links newspaper series; target links publication issues; M10. |
| `bf:productionMethod` | `ha:hasProductionMethod` | **REVIEW** | D | Target range ha:BibframeProductionMethod is undefined; M11. |
| `bf:succeededBy` | `ha:isSucceededBy` | **MAP** | D | — |
| `bf:supplement` | `ha:hasSupplement` | **MAP** | D | — |
| `bf:supplementTo` | `ha:isSupplementTo` | **MAP** | D | — |
| `dct:available` | `ha:hasAvailabilityDate` | **REVIEW** | D | xsd:dateTime to EDTF-level1; preserve precision; M06. |
| `dct:description` | `ha:hasDescription` | **MAP** | G | — |
| `dct:format` | `ha:hasFormat` | **REVIEW** | D, O | Split file-format IRIs from intellectual-entity format strings; M03. |
| `dct:license` | `ha:hasLicense` | **REVIEW** | R | Digital-representation usage conflicts with target domain; M17. |
| `dct:rights` | `ha:hasRights` | **CHANGE** | D, R | Preserve both text and statement IRIs; do not conflate them; M14/M17. |
| `foaf:homepage` | `ha:hasHomepage` | **CHANGE** | G | Source IRI becomes an xsd:anyURI literal if following the declared range; M07. |

### EBUCore, ordering and preservation relationship properties

| Source term | Target term / action | Status | Used in | Notes |
| --- | --- | --- | --- | --- |
| `ebucore:annotationConfidence` | `ha:hasAnnotationConfidence` | **MAP** | D | — |
| `ebucore:annotationType` | `ha:hasAnnotationType` | **CHANGE** | D | Keep concept IRI; type the selected concept as ha:AnnotationType; M09. |
| `ebucore:hasAnnotationRelatedAgent` | `ha:hasAnnotationSubject` | **CHANGE** | D | Merge subject links while recording their original predicates; M09. |
| `ebucore:hasAnnotationRelatedArtefact` | `ha:hasAnnotationSubject` | **CHANGE** | D | Merge subject links while recording their original predicates; M09. |
| `ebucore:hasAnnotationTarget` | `ha:hasAnnotationTarget` | **MAP** | D | — |
| `ebucore:hasCaptioning` | `ha:hasCaptioning` | **REVIEW** | D | Choose accessibility captioning or subtitling; source also allows file objects and reels; M08. |
| `ebucore:hasCastMember` | `ha:hasCastMember` | **REVIEW** | D | Source string becomes a structured cast entry; identity cannot be inferred safely; M02. |
| `ebucore:hasMediaFragment` | `ha:hasMediaFragment` | **REVIEW** | D, O | Both fragment classes converge under the target equivalence; M04. |
| `ebucore:hasMimeType` | `ha:hasMimeType` | **REVIEW** | O | Predicate is clear; target subPropertyOf ha:hasFormat creates a range conflict; M03. |
| `ebucore:hasObjectType` | `ha:hasObjectType` | **MAP** | D | — |
| `ebucore:height` | `ha:hasHeight` | **REVIEW** | D | Integer literal becomes a measurement node; unit must be known; M05. |
| `ebucore:isAnnotatedMediaResource` | `ha:annotatesMediaResource` | **REVIEW** | D | Keep direction; target expects ha:MediaResource, with a broken fragment hierarchy; M04/M09. |
| `ebucore:isMediaFragmentOf` | `ha:isMediaFragmentOf` | **REVIEW** | D, O | Source object is premis:File; target expects ha:MediaResource; M04. |
| `ebucore:regionDelimX` | `ha:hasRegionX` | **CHANGE** | D | Validate nonnegative pixel coordinates; reject negative or unknown-unit values; M05. |
| `ebucore:regionDelimY` | `ha:hasRegionY` | **REVIEW** | D | Semantic candidate; target seeAlso names ebucore:regionY instead; validate pixels; M05. |
| `ebucore:synopsis` | `ha:hasSynopsis` | **REVIEW** | D | String range conflicts with its rdf:langString superproperty; M07. |
| `ebucore:width` | `ha:hasWidth` | **REVIEW** | D | Integer literal becomes a measurement node; unit must be known; M05. |
| `edm:isNextInSequence` | `ha:immediatelyFollows` | **MAP** | O | Keep subject/object order: later resource to immediately preceding resource. |
| `evtAgRole:exe` | `ha:hasExecutingSoftware` | **MAP** | E | — |
| `evtAgRole:imp` | `ha:isImplementedBy` | **MAP** | E | Organization remains the implementer, retyped as ha:Organization. |
| `evtObjRole:out` | `ha:hasOutput` | **MAP** | E | Event to preservation object; preserve direction. |
| `evtObjRole:sou` | `ha:hasEventInput` | **MAP** | E | Event to input preservation object; preserve direction. |
| `rel:doc` | `ha:documents` | **MAP** | O | — |
| `rel:hsp` | `ha:hasStructuralPart` | **MAP** | D, O | — |
| `rel:hsr` | `ha:hasRenderingRoot` | **MAP** | O | — |
| `rel:hss` | `ha:hasDerivationSource` | **MAP** | O | — |
| `rel:inc` | `ha:includes` | **MAP** | O | — |
| `rel:isi` | `ha:isIncludedIn` | **MAP** | D, O | Keep direction, including the source DVD-chapter to DVD usage. |
| `rel:isp` | `ha:isStructuralPartOf` | **MAP** | D, O | — |
| `rel:isr` | `ha:isRepresentedBy` | **MAP** | O | — |
| `rel:rep` | `ha:represents` | **MAP** | O | — |
| `rel:sup` | `ha:supersedes` | **MAP** | O | — |

### ODRL, PREMIS, PROV, RDF and SKOS properties

| Source term | Target term / action | Status | Used in | Notes |
| --- | --- | --- | --- | --- |
| `odrl:action` | `odrl:action` | **KEEP** | R | Preserve the external predicate. |
| `odrl:constraint` | `odrl:constraint` | **KEEP** | R | Preserve the external predicate. |
| `odrl:hasPolicy` | `odrl:hasPolicy` | **KEEP** | R | Preserve the external predicate. |
| `odrl:leftOperand` | `odrl:leftOperand` | **KEEP** | R | Preserve the external predicate. |
| `odrl:operator` | `odrl:operator` | **KEEP** | R | Preserve the external predicate. |
| `odrl:permission` | `odrl:permission` | **KEEP** | R | Preserve the external predicate. |
| `odrl:prohibition` | `odrl:prohibition` | **KEEP** | R | Preserve the external predicate. |
| `odrl:rightOperand` | `odrl:rightOperand` | **KEEP** | R | Preserve the external predicate. |
| `odrl:target` | `odrl:target` | **KEEP** | R | Preserve the external predicate. |
| `premis:basis` | `premis:basis` | **KEEP** | R | Retain; retype rights-statement objects and review RightsBasis hierarchy; M17. |
| `premis:endDate` | `premis:endDate` | **KEEP** | R | Preserve the external predicate. |
| `premis:fixity` | `premis:fixity` | **KEEP** | O | Preserve the external predicate. |
| `premis:identifier` | `premis:identifier` | **KEEP** | O | Retain all generic local-identifier links; do not mark all of them primary; M01. |
| `premis:medium` | `premis:medium` | **KEEP** | O | Preserve the external predicate. |
| `premis:note` | `premis:note` | **KEEP** | E, R | Preserve the external predicate. |
| `premis:originalName` | `premis:originalName` | **KEEP** | O | Preserve the external predicate. |
| `premis:outcome` | `premis:outcome` | **KEEP** | E | Preserve the external predicate. |
| `premis:outcomeNote` | `premis:outcomeNote` | **KEEP** | E | Preserve the external predicate. |
| `premis:relationship` | `premis:relationship` | **KEEP** | O | Generic relationship remains generic; do not invent a specific relation subtype. |
| `premis:rightsStatus` | `premis:rightsStatus` | **KEEP** | R | Preserve status nodes; public-domain class/value distinction needs review; M17. |
| `premis:size` | `premis:size` | **KEEP** | O | Preserve the external predicate. |
| `premis:startDate` | `premis:startDate` | **KEEP** | R | Preserve the external predicate. |
| `premis:storedAt` | `premis:storedAt` | **KEEP** | D, O | Retain on carrier representations and files; retype linked carriers only. |
| `prov:endedAtTime` | `prov:endedAtTime` | **KEEP** | E | Preserve the external predicate. |
| `prov:generated` | `prov:generated` | **KEEP** | E | Keep on generic activities; ha:hasOutput is optional only for event-to-object links; M13. |
| `prov:startedAtTime` | `prov:startedAtTime` | **KEEP** | E | Preserve the external predicate. |
| `prov:wasAssociatedWith` | `prov:wasAssociatedWith` | **KEEP** | E | Preserve the external predicate. |
| `prov:wasDerivedFrom` | No supported target for the source usage | **UNMAPPED** | O | Absent from the target PROV extract; source points to Mediahaven metadata, not a preservation object; M13. |
| `prov:wasGeneratedBy` | `prov:wasGeneratedBy` | **KEEP** | E | Preserve the external predicate. |
| `rdf:value` | `rdf:value` | **KEEP** | O | Keep on fixity, storage locations and local identifiers; never rename globally; M01/M05. |
| `skos:altLabel` | `ha:hasAlternateName` on organizations (proposed) | **REVIEW** | G | Organization-name candidate; preserve all languages pending policy; M07. |
| `skos:prefLabel` | `ha:hasName` on organizations (proposed); `skos:prefLabel` on concepts | **REVIEW** | G | Organization names may become ha:hasName; role-type concept labels stay SKOS; M02/M07. |

## Decisions and transformation rules

These are findings about the supplied files. Proposed ontology corrections are prerequisites for a later migration, not edits made by this report.

### M01 — Separate literal identifiers, local identifier nodes and primary identifiers

The source has three distinct patterns:

- `schema:identifier` and `org:identifier` carry string literals, including technical identifiers for files, representations and Mediahaven records.
- `premis:identifier` links an intellectual entity to one or more `haObj:LocalIdentifier` nodes. Keep this predicate, retype those nodes to `ha:LocalIdentifier`, and keep each node's `rdf:value` string.
- `haObj:primaryIdentifier` selects the primary local identifier. Rename only this link to `ha:hasPrimaryLocalIdentifier`.

The target `ha:hasIdentifier` is declared an `owl:DatatypeProperty` but has the resource class `ha:LocalIdentifier` as its range (`hetarchief/model.rdfs.ttl:2514`). This does not settle whether source strings must stay literals or become identifier nodes. **REVIEW:** choose one representation before converting them. The least disruptive option is to keep technical identifiers as strings under `ha:hasIdentifier`, with the target range corrected by the model owner, while preserving the existing PREMIS local-identifier structure. If resource-valued identifiers are intended instead, the property kind must change and literal identifiers need deterministic nodes carrying the original string and identifier-system context.

Never promote every `premis:identifier` value to primary, merge identifiers merely because their string values match, or discard leading zeroes. The target makes `ha:hasSerialNumber` a subproperty of `ha:hasIdentifier`, so the same conflict affects serial numbers. Keep `rdf:value` on identifiers, checksums and storage locations; its use on measurements is a separate context in M05.

### M02 — Preserve contribution roles and distinguish role assignments from role types

The source repeats contribution predicates on two levels: `work → role → agent` (`description/description.shacl.ttl:140` and `description/description.shacl.ttl:1837`). A global predicate replacement would make the role node another work or intellectual entity through the target domains.

For a contextual contribution:

1. Preserve the existing role node's identity and map its class to `ha:Role` or, where justified, `ha:PerformanceRole`.
2. Rename the incoming work predicate to `ha:hasCreator`, `ha:hasContributor`, `ha:hasPublisher`, `ha:hasProducer` or `ha:hasExecutor`, as appropriate.
3. Replace the role's outgoing `schema:creator`, `schema:contributor`, `schema:publisher`, `schema:producer`, `schema:actor` or `haDes:executor` agent link with `rdf:value`. The target explicitly specifies this agent-link pattern for `ha:Role` (`hetarchief/model.rdfs.ttl:550`).
4. Preserve `schema:characterName` as `ha:hasCharacterName`. Convert concept-valued `schema:roleName` to `ha:hasRoleType`, and retype its `haDes:RoleName` object as `ha:RoleType`.

For example, subject to the role decisions below, this preserves a creator assignment:

```turtle
# Before
:work schema:creator :credit .
:credit a schema:Role ;
    schema:creator :person ;
    schema:roleName :director .

# After
:work ha:hasCreator :credit .
:credit a ha:Role ;
    rdf:value :person ;
    ha:hasRoleType :director .
:director a ha:RoleType .
```

**REVIEW:** free-text role names need approved role-type concepts; do not turn a string directly into an IRI. The source permits generic `schema:Thing` agents, while several target ranges require persons, organizations or agents. Preserve unresolved identities rather than guessing their class.

**REVIEW:** `schema:actor` links a work to `schema:PerformanceRole`, but `ha:hasActor` ranges only over `ha:Person` (`hetarchief/model.rdfs.ttl:725`). Resolve whether its range should allow role nodes, or whether cast assignments should use `ha:hasCastMember` and `ha:CastMemberEntry`. Flattening to the person would lose the character and role context. Likewise, source `ebucore:hasCastMember` is a string, while the target range is `ha:CastMemberEntry`; preserve the textual credit until a reliable structured entry can be produced.

For organizational functions, `org:Role` means an abstract SKOS concept (`ontologies/org.rdfs.ttl:45`). `ha:RoleType` is therefore the recommended semantic candidate, and `org:role` would become `ha:hasRoleType`. However, the target `ha:Role` explicitly references `org:Role`. **REVIEW:** confirm that separation before changing class assertions. Keep `skos:prefLabel` on role-type concepts. The target also spells the Post hierarchy as `rdf:subClassOf`, which does not establish an RDFS subclass (`hetarchief/model.rdfs.ttl:479`); its relationship to `ha:Role` needs correction or an explicit typing policy.

### M03 — Split the two uses of dct:format

On files, source `dct:format` points to a `dct:FileFormat` resource. Preserve that resource's IRI and retype it to `ha:FileFormat`; that class has an explicit equivalence in the target. The candidate predicate is `ha:hasFormat`, but its range is **undefined `ha:Format`**, rather than the declared `ha:FileFormat` (`hetarchief/model.rdfs.ttl:2505`). **REVIEW:** settle the range before generating file-format links.

On intellectual entities, `dct:format` is one of nine strings (`description/description.shacl.ttl:464`). These are content classifications, not file-format entities. The following are candidate class derivations, not blanket replacements of the format value:

| Source string | Candidate target treatment | Confidence / limitation |
| --- | --- | --- |
| `audio` | Add `rdf:type ha:Audio` | Clear content-class candidate. |
| `video` | Add `rdf:type ha:Video` | Clear content-class candidate. |
| `film` | Add `rdf:type ha:Film` | Clear content-class candidate. |
| `image` | Add `rdf:type ha:Image` | Clear content-class candidate. |
| `paper` | Possibly `ha:Document` | **REVIEW:** paper material does not by itself establish document semantics. |
| `newspaper` | Possibly `ha:NewspaperIssue` or `ha:Newspaper` | **REVIEW:** distinguish an individual issue from the newspaper series. |
| `newspaperpage` | Add `rdf:type ha:NewspaperIssuePage` | Strong candidate; check parent-issue links. |
| `videofragment` | Classify the intellectual content and model its fragment representation separately | **REVIEW:** no dedicated target video-fragment intellectual-entity class. |
| `audiofragment` | Classify the intellectual content and model its fragment representation separately | **REVIEW:** no dedicated target audio-fragment intellectual-entity class. |

Keep the original classification in the migration provenance until its disposition is approved. Do not replace these strings with `ha:FileFormat` instances or turn an intellectual entity into a representation solely because its format says “fragment”.

`ebucore:hasMimeType → ha:hasMimeType` is a clear lexical match, but `ha:hasMimeType` has string values and is a subproperty of `ha:hasFormat`; the latter's class range therefore also affects MIME literals. Resolve this target relationship with the format range.

### M04 — Convert fragment times to offsets and resolve fragment hierarchy

The source uses `schema:startTime` and `schema:endTime` as `xsd:time` on both `haObj:FragmentRepresentation` and `ebucore:MediaFragment`. The target `ha:hasStartOffset` and `ha:hasEndOffset` require **integer seconds relative to the start of the source media** (`hetarchief/model.rdfs.ttl:1087` and `hetarchief/model.rdfs.ttl:1659`).

Once the source values are confirmed to be relative offsets, convert `HH:MM:SS` to `3600 × HH + 60 × MM + SS`; for example, `00:01:30` becomes `90`. **REVIEW:** fractional seconds, time zones, wall-clock values and wrapped times cannot be converted safely under that integer model without additional decisions. Do not round silently or manufacture a media-start reference. Keep `schema:duration → ha:hasDuration` as `xsd:duration`.

The target equates `ha:FragmentRepresentation` and `ha:MediaFragment`, making every media fragment a digital representation under OWL equivalence (`hetarchief/model.rdfs.ttl:315`). Also, `ha:MediaFragment` uses `rdfs:subPropertyOf ha:MediaResource` rather than a class hierarchy (`hetarchief/model.rdfs.ttl:372`). **REVIEW:** confirm whether geometric/annotation fragments should all be representations and resolve the hierarchy.

Both `ha:isMediaFragmentOf` and `ha:annotatesMediaResource` expect `ha:MediaResource`. The source former relation points to `premis:File`; the latter points to a media fragment. The target does not establish the required class relationships. Decide whether qualifying files/fragments receive explicit `ha:MediaResource` types or the ranges/hierarchy change. Do not classify every file as audiovisual media. Preserve all relation directions.

### M05 — Preserve measurement structure and units

Existing `schema:QuantitativeValue` nodes become `ha:QuantitativeValue`. Map `schema:value` to `ha:hasMeasurementValue`, and rename the unit predicates to `ha:hasUnitCode` and `ha:hasUnitText`. Keep unit codes and numeric precision; do not recalculate measurements merely to rename predicates.

`ebucore:width` and `ebucore:height` are integer literals on source media fragments. Their target properties expect measurement nodes. **REVIEW:** create a measurement node only when its unit is known from the data or authoritative context; the source descriptions allow pixels or physical dimensions. The new node must preserve the original value and use the approved unit. Source file-level width/height links already point to measurement nodes and need no such wrapping.

The target width/height domain unions omit `premis:File`, although source shapes use them on files. `ha:hasHeight` also contains the misspelling `owl:unionOF` (`hetarchief/model.rdfs.ttl:1138`). Resolve these declarations before applying strict validation or drawing class inferences from dimensions.

For region coordinates, validate that values are nonnegative and measured in pixels before emitting `ha:hasRegionX` / `ha:hasRegionY`. The Y mapping is semantic: its target `seeAlso` points to `ebucore:regionY`, not the actual source `ebucore:regionDelimY`.

For audio speed, preserve existing `/id/rotational-speed/` IRIs. The supporting SKOS file uses `http://schema.org/QualitativeValue`, whereas the shape requires `https://schema.org/QuantitativeValue`. Numeric entries carry usable value/unit facts and can be normalized deliberately. **REVIEW:** the `variable` concept has no numeric measurement, so do not invent a float or treat it as an ordinary quantitative value.

Finally, `ha:hasMeasurementValue` is globally `owl:equivalentProperty rdf:value` (`hetarchief/model.rdfs.ttl:1603`). Under OWL reasoning this would also treat identifier strings, checksums, location values and role-agent links as float-valued measurements. **REVIEW:** narrow/remove that equivalence in a separately approved model revision, or explicitly exclude that entailment pending resolution. A context-sensitive migration must never implement it as a global `rdf:value` rename.

### M06 — Preserve date precision

| Source usage | Target | Required treatment |
| --- | --- | --- |
| `schema:dateCreated`: EDTF levels 0/1/2 | `ha:hasCreationDate`: `xsd:dateTime` | **REVIEW:** convert only values that actually contain the required complete date/time information. |
| `schema:datePublished`: EDTF levels 0/1/2 | `ha:hasPublicationDate`: EDTF level 1 | **REVIEW:** prove lexical/semantic compatibility before changing the datatype; preserve level-2 expressions that cannot be represented. |
| `schema:copyrightYear`: integer | `ha:hasCopyrightDate`: `xsd:dateTime` | **REVIEW:** a year does not identify a day or time. A model change or a separate year representation is required. |
| `dct:available`: `xsd:dateTime` | `ha:hasAvailabilityDate`: EDTF level 1 | **REVIEW:** preserve any time/zone information that the chosen target representation cannot express. |
| `schema:birthDate`, `schema:deathDate`: EDTF level 1 | `ha:hasBirthDate`, `ha:hasDeathDate`: EDTF level 1 | Rename without losing date uncertainty. |
| `schema:startDate`, `schema:endDate` on newspapers | `ha:hasStartDate`, `ha:hasEndDate`: `xsd:dateTime` | Rename and preserve the literal. |
| Mediahaven `schema:dateDeleted`, `schema:dateModified` | `ha:hasDeletionDate`, `ha:hasModificationDate`: `xsd:dateTime` | Rename and preserve the timestamp. |
| Rights `premis:startDate`, `premis:endDate` | Same predicates | Keep the source `xsd:dateTime` literals. |

The target creation-date domain omits source file and Mediahaven-fragment subjects; publication-date domain omits source digital representations. Resolve those domain gaps rather than moving a timestamp to a different entity. Never fill in 1 January, midnight or a timezone to satisfy a datatype. Evidence: `description/description.shacl.ttl:107`, `objects/objects.shacl.ttl:1125`, and the corresponding target date-property definitions.

### M07 — Preserve multilingual text, language codes and URI node kinds

Most source `schema:name` values, organization `skos:prefLabel` / `skos:altLabel`, and descriptive fields are `rdf:langString`. The target ranges for `ha:hasName`, `ha:hasAlternateName`, `ha:hasAbstract`, `ha:hasGenre`, `ha:hasKeywords`, `ha:hasTemporal`, `ha:hasArtform`, `ha:hasArtMedium` and `ha:hasCreditText` are `xsd:string`. **REVIEW:** keep every language-tagged value until the model owner chooses a language-preserving representation. Stripping tags can collapse distinct values and lose meaning. `ha:hasDescription` already has the compatible `rdf:langString` range.

For organization labels, `ha:hasName` and `ha:hasAlternateName` are semantic candidates; the target does not explicitly map the SKOS label properties. Keep SKOS labels on concepts, especially `ha:RoleType`, rather than renaming all occurrences globally.

The target `ha:hasAbstract` and `ha:hasSynopsis` have `xsd:string` ranges but are subproperties of `ha:hasDescription`, whose range is `rdf:langString`. That inheritance also needs resolution. The target and imported PREMIS notes additionally reference undefined `ha:description`; do not substitute it for the declared `ha:hasDescription`.

`schema:inLanguage` strings become `ha:hasLanguage` with `xsd:language`; validate the lexical form and normalize only with evidence. The target domain is an intellectual entity, while source usage also covers digital representations and open captions. Resolve that domain mismatch.

Source `foaf:homepage` and `schema:thumbnailUrl` values are IRIs, while their target ranges are `xsd:anyURI`. If the target's literal representation is retained, convert the exact IRI string to an `xsd:anyURI` literal and update consumers accordingly. If links should remain RDF resources, the target ranges need adjustment instead. Do not silently mix the two representations.

### M08 — Distinguish captioning, subtitles, caption text and transcripts

The source uses `ebucore:hasCaptioning` for files and image reels, allowing a file or closed-caption object in the former case and open captions in the latter. The target separates accessibility captions (`ha:Captioning`, `ha:ClosedCaptions`, `ha:OpenCaptions`) from general subtitles (`ha:Subtitling`, `ha:ClosedSubtitling`, `ha:OpenSubtitling`). Its comments explicitly leave the replacement question open (`hetarchief/model.rdfs.ttl:118`).

**REVIEW:** classify each existing caption object by actual purpose; do not assume all subtitles are accessibility captions. Choose the matching `ha:hasCaptioning` or `ha:hasSubtitling` link. A detached subtitle file can be `ha:ClosedSubtitling` only when its role is established. Both link properties currently have `premis:File` domains, which do not fit image-reel subjects.

`schema:caption` is a plain textual caption on a digital representation. Its candidate `ha:hasCaptionText` has an undefined `ha:File` domain, and it should not be confused with captioning resources. `schema:transcript → ha:hasTranscript` also changes from a digital-representation subject to a target intellectual-entity domain. Resolve those subject models while preserving each text on its original resource.

### M09 — Merge annotation subjects while retaining provenance

Map both `ebucore:hasAnnotationRelatedArtefact` and `ebucore:hasAnnotationRelatedAgent` to `ha:hasAnnotationSubject`, keeping the referenced resource IRIs. The source permits one artefact and an additional agent; retain both when they differ. When both old predicates have the same object, RDF deduplication will leave one target triple. Record the original predicates in migration provenance if their distinction is needed.

Retype only concepts actually used as `ebucore:annotationType` values to `ha:AnnotationType`; do not retype every SKOS concept. Preserve `ebucore:annotationConfidence → ha:hasAnnotationConfidence` as a decimal. Keep the target file link (`ha:hasAnnotationTarget`) distinct from the annotated fragment/resource link (`ha:annotatesMediaResource`); they express different relationships. Resolve the resource hierarchy described in M04.

### M10 — Keep grouping, structural membership and publication sequencing distinct

`schema:CreativeWork` appears as a permitted value class but has no single corresponding generic class in the target. Existing explicit series, season, collection, archive-component and newspaper types have the tabled destinations. **REVIEW:** a resource known only as `schema:CreativeWork` must be classified as a grouping or an individual intellectual work before a replacement class is chosen.

Keep the source distinction between generic `schema:hasPart` / `schema:isPartOf` and PREMIS structural relationships `rel:hsp` / `rel:isp`. They map to `ha:hasPart` / `ha:isPartOf` and `ha:hasStructuralPart` / `ha:isStructuralPartOf`, respectively. Cross-category preservation inclusion uses `ha:includes` / `ha:isIncludedIn`. Do not collapse these relationships.

The target `ha:isPartOf` domain permits only intellectual entities, but the source also uses it on series, seasons and archive components, which migrate to collections. `ha:hasPosition` similarly has an intellectual-entity domain but is used for source series. These class effects need a policy; do not manufacture intellectual-entity types for all groupings as a side effect of migration.

The source `bf:precededBy` links newspaper series; target `ha:isPrecededBy` links `ha:PublicationIssue` instances. **REVIEW:** this is not a safe series-level rename, even though the target references the same external predicate. In contrast, `bf:succeededBy`, `bf:supplement` and `bf:supplementTo` have target newspaper-to-newspaper definitions matching the source context.

`ha:hasIssueNumber` has no direct range, but its superproperty `ha:hasPosition` ranges over integers; the source allows strings such as numbered or alphanumeric designations. Preserve the string and resolve the inherited range. The target also does not explicitly make `ha:NewspaperIssue` a subclass of `ha:PublicationIssue`, although issuance/edition/issue-number domains use the latter. Decide the intended hierarchy or explicit dual typing before validation.

For `edm:isNextInSequence → ha:immediatelyFollows`, preserve direction: **the subject follows the object**. This agrees with the legacy EDM definition (`ontologies/edm.rdfs.ttl:12`); do not reverse the edge based on the English name alone.

### M11 — Resolve production method, edition and issuance semantics

The `bf:productionMethod → ha:hasProductionMethod` candidate is clear, but its target range is undefined `ha:BibframeProductionMethod`. The declared concept class is `ha:ProductionMethod` (`hetarchief/model.rdfs.ttl:1503` and `hetarchief/model.rdfs.ttl:1906`). **REVIEW:** settle the range, then retain the existing production-method concept IRIs and add the agreed target type.

`bf:edition → ha:hasEdition` preserves edition-type concept objects, but the target declares `ha:hasEdition` as an `owl:DatatypeProperty` while ranging over `skos:Concept`. **REVIEW:** an IRI-valued edition link needs an appropriate property declaration.

Source `bf:issuance` explicitly means publication **frequency**, such as daily or weekly (`description/description.shacl.ttl:1140`). Target `ha:Issuance` instead describes **mode of issuance**, such as whether a publication ends or is updated in parts. The similar name does not establish a lossless mapping. **REVIEW:** inspect the actual concepts. Map only genuine mode-of-issuance values to `ha:hasIssuance` / `ha:Issuance`; no adequate target frequency property was identified for frequency values. Preserve those source statements pending a model decision.

### M12 — Resolve literal places and countries without guessing identity

Source birth/death places are strings, whereas target properties expect place resources. Address country can be a string or a `schema:Country` resource. Keep existing resource identities and apply the class mappings; resolve strings through an approved place/country authority or a documented local-node policy, preserving their original text. Do not merge ambiguous place names merely because they match lexically.

`ha:hasBirthPlace` still ranges over external `schema:Place`, while the class crosswalk maps it to `ha:Place`; death place and creation place use `ha:Place`. **REVIEW:** settle consistent local/external typing. Also, `ha:hasSpatial` ranges over `ha:Place` but is a subproperty of string-valued `ha:hasCoverage`, which conflicts with those object links. Source newspaper creation-place links additionally need the grouping-domain decision from M10.

### M13 — Keep generic provenance broader than preservation-event links

`prov:wasDerivedFrom` is used from intellectual entities, representations and files to `mh:Fragment` metadata records (`objects/objects.shacl.ttl:304`). That predicate is not defined in the supplied target PROV extract. `ha:hasDerivationSource` is not a safe substitute: it links preservation objects to preservation objects, while `ha:MediahavenFragment` describes the metadata-system fragment. The target itself raises the question of a generic derivation property (`hetarchief/model.rdfs.ttl:1465`). **UNMAPPED:** preserve these provenance links until the model explicitly retains/imports the PROV property or defines a suitable alternative. The Mediahaven fragment class and its record relation can migrate independently.

Keep `prov:generated` on generic `prov:Activity` instances. Only an established preservation-event-to-object link is eligible for the more specific `ha:hasOutput`; the original `evtObjRole:out` already maps there directly. Do not narrow arbitrary generated IRIs to preservation objects.

The source also uses `schema:creator` as a **string on `premis:Fixity`** (`objects/objects.shacl.ttl:1003`). `ha:hasCreator` expects an agent/role and a work or digital-representation subject. **REVIEW:** this context has no safe direct conversion. Identify the checksum-generating agent and choose an approved attribution/provenance representation, or retain the original string in the legacy graph. Never convert it with the work/role rule blindly.

### M14 — Preserve copyright notices separately from general rights text

No dedicated target equivalent of `schema:copyrightNotice` was identified. `ha:hasRights` is a possible broader container, but combining notices with general source `dct:rights` text loses the distinction. **UNMAPPED:** preserve notices under their original predicate pending a decision to keep an external notice term, add a dedicated target term, or explicitly accept a broader mapping with provenance.

`dct:rights → ha:hasRights` itself is supported. In D it carries text; in R it points to a rights-statement resource. Preserve the RDF node kind and both values when both exist. Do not stringify statement IRIs or replace free text with an arbitrary controlled statement.

### M15 — Review request-form links versus templates

`haOrg:requestForm` describes a string containing the URL of a request form. `ha:hasContentRequestFormTemplate` explicitly describes a URI template whose placeholders are replaced with content-specific values. **REVIEW:** a plain URL may be usable as a constant template, but that behavior must be confirmed in the application. Preserve existing placeholders verbatim where present; do not invent item parameters. Evidence: `organizations/organizations.rdfs.ttl:144` and `hetarchief/model.rdfs.ttl:1545`.

### M16 — Preserve inverse access-copy direction

Map `haObj:isAccessCopyOf` directly to `ha:isAccessCopyOf`: digital representation → intellectual entity. The current workspace target declares domain `ha:DigitalRepresentation`, range `premis:IntellectualEntity`, and inverse `ha:hasAccessCopy` (`hetarchief/model.rdfs.ttl:2131`), which agree with this direction. Preserve the source edge; check its inverse against the corresponding intellectual-entity-to-representation link.

### M17 — Migrate rights values as well as predicates

Keep the ODRL graph structure: policy → permission/prohibition → action/constraint, constraint → left operand/operator/right operand, and policy → target. Keeping ODRL predicates does not mean keeping all operand IRIs. Apply the exact value crosswalk in the next section, including occurrences in reusable permission vocabularies.

`ha:extended` and `ha:limited` still have the undefined type `ha:MetadataRange`, despite the declared class being `ha:MetadataScope`. Source `sh:in` also permits action concepts as right operands while its `sh:class` alternatives only cover user groups and metadata/content scopes. **REVIEW:** settle those allowed-value/type combinations and the target ODRL extract's datatype-property declaration for IRI-valued `odrl:rightOperand`; do not carry over inconsistent constraints blindly.

The source uses `copyrightStatus:pub` in `sh:class`; the target explicitly equates it with class `ha:PublicDomainStatus`. That supports a class mapping, but does not make a target class IRI a rights-status instance. **REVIEW:** distinguish existing status nodes typed with the source class from direct vocabulary-value objects. A direct public-domain value may require a status node typed `ha:PublicDomainStatus`; do not emit `premis:rightsStatus ha:PublicDomainStatus` as a shortcut.

Retype `dct:RightsStatement` resources to `ha:RightsStatement`, preserving their IRIs and SKOS data. Keep `premis:License`, `premis:RightsStatus`, `premis:basis`, `premis:note`, `premis:startDate` and `premis:endDate`. The target `premis:basis` ranges over `premis:RightsBasis`, but the supplied definitions do not connect `ha:RightsStatement` or `premis:License` to that superclass; establish an agreed hierarchy or typing policy. The target `ha:hasLicense` has an intellectual-entity domain, although source `dct:license` also occurs on digital representations. Do not move a representation's license to its intellectual entity automatically.

The target makes `ha:hasLicense` equivalent to `ha:hasAccessRights`; do not use that declaration as a reason to collapse license information, access policies and rights-status records during data conversion.

## Controlled-value crosswalk

These values occur directly in the source shapes' active `sh:in` lists. They are data resources, not new class/property counts. Apply their mappings in object positions and wherever those same vocabulary resources are described or referenced; do not perform a blanket namespace replacement on unrelated instance IRIs.

### Rights operands, actions and event outcomes

| Source value | Target value | Status / note |
| --- | --- | --- |
| `haRig:metadataRange` | `ha:metadataScopeOperand` | MAP; left operand, distinct from the scope class. |
| `haRig:contentRange` | `ha:contentScopeOperand` | MAP; left operand, distinct from the scope class. |
| `haRig:extended` | `ha:extended` | REVIEW; target still types it as undefined `ha:MetadataRange`; M17. |
| `haRig:limited` | `ha:limited` | REVIEW; same target typing issue; M17. |
| `haRig:full` | `ha:full` | MAP. |
| `haRig:partial` | `ha:partial` | MAP. |
| `haRig:available-for-consultation` | `ha:availableForConsultation` | MAP; action; review source right-operand usage separately. |
| `haRig:downloadable` | `ha:downloadable` | MAP; action; review source right-operand usage separately. |
| `haRig:between-partners` | `ha:betweenPartners` | MAP. |
| `haRig:educational-public` | `ha:educationalPublic` | MAP. |
| `haRig:intra-muros` | `ha:intraMuros` | MAP. |
| `haRig:public` | `ha:public` | MAP. |
| `haRig:research-public` | `ha:researchPublic` | MAP. |
| `odrl:eq` | `odrl:eq` | KEEP; imported operator. |
| `odrl:lt` | `odrl:lt` | KEEP; imported operator. |
| `odrl:recipient` | `odrl:recipient` | KEEP; imported left operand. |
| `odrl:dateTime` | `odrl:dateTime` | KEEP; imported left operand. |
| `odrl:absoluteTemporalPosition` | `odrl:absoluteTemporalPosition` | KEEP; imported left operand. |
| `evtOutcome:fai` | `ha:fail` | CHANGE; target does not explicitly type it as `premis:OutcomeStatus`; add agreed type or resolve vocabulary typing. |
| `evtOutcome:suc` | `ha:success` | CHANGE; same outcome-status typing issue. |
| `evtOutcome:war` | `ha:warning` | CHANGE; same outcome-status typing issue. |

The three event outcome candidates have matching target `seeAlso` references and definitions. Preserve their intended `premis:OutcomeStatus` role, rather than changing `premis:outcome` to a literal success flag.

### Other enumerations and stable concept identities

| Source values | Migration action | Status / note |
| --- | --- | --- |
| `https://data.hetarchief.be/id/iec60094-type/` with local names `I`, `II`, `III`, `IV` | Keep all four IRIs under `ha:hasIEC60094Type`. | KEEP; retain SKOS labels and scheme. |
| `https://data.hetarchief.be/id/rotational-speed/` with local names `variable`, `16-rpm`, `19-cm-s`, `2.375-cm-s`, `33-1-3-rpm`, `38-cm-s`, `4.75-cm-s`, `72-cm-s`, `78-rpm`, `90-rpm`, `9.5-cm-s` | Keep all eleven IRIs under `ha:hasAudioRecordingSpeed`; normalize numeric measurement descriptions where justified. | REVIEW; `variable` and supporting vocabulary types need M05. |
| `"DBX"`, `"Dolby A"`, `"Dolby B"`, `"Dolby C"`, `"Dolby D"` | Keep the five string values under `ha:hasAudioNoiseReduction`. | KEEP. |
| `https://data.hetarchief.be/id/edition-type/` with local names `morning-edition`, `afternoon-edition`, `evening-edition`, `weekend-edition` | Keep all four concept IRIs under the agreed edition predicate. | REVIEW; target property-kind conflict; M11. |
| `https://data.hetarchief.be/id/production-method/` with local names `handwritten`, `typed`, `printed` | Keep all three concept IRIs; add the agreed production-method type. | REVIEW; undefined target range; M11. |
| `https://data.hetarchief.be/id/color-type/` with local names `BandW`, `Color`, `Colorized`, `Composite`, `Tinted`, `Toned`, `UnknownColorType` | Keep all seven IRIs under `ha:hasFilmColorType`. | KEEP. |
| The nine `dct:format` strings | Use the context-specific treatment in M03. | REVIEW; do not turn them into file-format IRIs. |

Other instance/concept IRIs remain stable unless explicitly listed above. For example, retain `/id/motivation/`, `/id/permission/`, license, rights-statement, organization-preference, carrier and file-format concept identities. Apply the class/property mappings to their descriptions where relevant, including `haRig:Motivation → ha:Motivation` on motivation concepts and renamed operands inside permission definitions. Preserve SKOS labels, definitions, scheme memberships and links on these resources. This preserves supporting vocabulary data without expanding the shape-derived class/property inventory into a full vocabulary migration audit.

## Execution plan

### 1. Record the model decisions before enabling affected rules

Assign the identifier/format/role/fragment decisions to the model owner; rights-value decisions also need the rights-model owner, and URI-template/URL representation decisions need application-owner input. Resolve M01–M17 against actual data examples. Record the accepted destination, condition, conversion, retained provenance and validation expectation for every REVIEW/UNMAPPED context. No guessed replacement should be enabled merely to remove all legacy IRIs.

The first blockers are identifier representation (M01), role structure (M02), format range/classification (M03), fragment offsets/hierarchy (M04), and preservation of multilingual/date precision (M06–M07). The remaining issues can be isolated by context while unaffected mappings proceed. Any ontology corrections are a separate change from this report.

### 2. Profile the source dataset and preserve a reproducible baseline

Freeze the source ontology/vocabulary versions and take a restorable copy or immutable source graph. Count explicit class assertions, predicates and controlled-value IRIs from this inventory. Also list observed terms outside it, because SHACL describes supported usage rather than proving which triples actually exist. Profile literal datatypes/languages, node kinds, role-wrapper patterns, identifier-system boundaries, dates, offset precision, measurement units, and cross-links to vocabulary resources.

Do not assume every source-shaped resource conforms: note existing violations separately from problems introduced by migration. Specifically check checksum creators, role agents that are generic things, variable recording speed, series-level predecessors, and public-domain values.

### 3. Apply deterministic class and predicate rules into a new graph

Use an explicit IRI map, with subject-type/context guards where specified. Preserve resource identities, blank-node structure where possible, inverse directions and relation subtypes. Apply KEEP rules as well as MAP rules so externally named data is not dropped. Apply controlled-value rewrites throughout relevant data and supporting vocabulary descriptions.

Do not load a broad equivalence closure as a substitute for explicit conversion: the target's measurement/RDF-value, fragment and datatype declarations need the decisions above. Deduplicate identical output triples while recording many-to-one merges. Leave source graphs unchanged and keep unresolved statements in an identifiable legacy/provenance graph.

### 4. Run the approved structural and literal conversions

Handle roles, identifier representation, measurements, media offsets, dates, place/country resolution and caption models using the approved M-rules. Use deterministic identifiers for any newly created nodes so rerunning the migration does not duplicate them. Preserve original lexical values, language tags, predicates and conversion reasons in migration records where representation changes.

A rule that cannot establish its preconditions must produce an exception record containing the source subject, predicate, object, source graph, issue ID and reason. It must not discard the statement, fabricate precision, or silently substitute a generic value.

### 5. Validate coverage, semantics and application behavior

Write migration-specific acceptance checks from the agreed mapping decisions and source requirements. Do not use the unfinished `hetarchief/model.shacl.ttl` as the acceptance authority.

| Check | Acceptance criterion |
| --- | --- |
| Inventory coverage | Every observed source class/property/value is mapped, explicitly kept, or reported as unresolved; no unclassified drops. |
| Target existence | Every emitted target class/property is declared in the model, one of its supplied imports, or an explicitly approved foundational/extension vocabulary. Undefined `ha:Format`, `ha:File`, `ha:BibframeProductionMethod` and `ha:MetadataRange` must not slip through as accidental destinations/types. |
| Value preservation | All multilingual texts, date precision, identifier lexical forms, checksum values, measurement units and status notes survive or have an explicit loss/exception decision. |
| Context rules | Work/role/agent chains remain navigable; checksum creators are not treated as work creators; generic generated resources and Mediahaven provenance are not narrowed to preservation objects. |
| Relations | Structural versus generic membership and inclusion remain distinct; inverse-copy edges remain consistent; sequence edges retain their direction. |
| Rights | Policy targets, actions, permissions/prohibitions, constraints and motivations retain their behavior; operand IRIs/types and public-domain status patterns are correct. |
| Counts | Reconcile changes using per-rule counts. Account explicitly for new measurement/identifier nodes and merged annotation-subject triples instead of requiring equal raw triple counts. |
| Repeatability | Rerunning against the same frozen input produces the same graph, no duplicate generated nodes and the same exception ledger. |
| Application checks | Compare representative searches, resource displays, collection navigation, media clips, captions, request forms and rights evaluations before and after migration. |

Run checks on a sample spanning all used shapes, then the full dataset. Test both the chosen explicit-data model and any reasoning profile the applications actually use; domain/range inferences must not accidentally turn collections into intellectual works or identifier values into measurements.

### 6. Cut over only after reconciliation

Keep a mapping-version identifier, baseline counts, conversion/exception totals and validation results with the migrated graph. Update affected producers, queries, indexes and applications against the concrete crosswalk, then perform a staged read comparison. Resolve or explicitly accept remaining exceptions before retiring legacy reads. Keep the old graph available for rollback until operational checks pass; removal of old data is a separate deployment decision.

## Deliverable verification and limits

All five source shape files, the target RDFS model and its three supplied external extracts were parsed as Turtle. The crosswalk contains one entry for each of the **90 classes and 211 properties** found through active shape statements. Every active source `sh:in` enumeration is accounted for in the controlled-value sections. Direct MAP/CHANGE/KEEP destinations were checked for declaration in the inspected target definitions, with the explicitly retained foundational RDF/SKOS terms allowed.

This report does not execute a data migration, amend the ontology, validate production instances, or resolve model-owner choices without evidence. The marked REVIEW/UNMAPPED cases remain material limits on a fully automatic migration.
