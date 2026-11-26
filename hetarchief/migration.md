# Migration legacy ontologies to the new hetarchief model

Prepared from the workspace sources on 24 November 2026 and revised against the current RDFS, SHACL and SKOS files on 26 November 2026.

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

The crosswalk uses the RDFS model and the target vocabularies in `hetarchief/terms/` to determine target mappings. The draft `hetarchief/model.shacl.ttl` needs alignment before migration acceptance. Regenerate `hetarchief/model.linkml.yaml` after that alignment. The current export still gives `hasProductionMethod` the older `BibframeProductionMethod` range. Production data profiling is part of the execution plan.

An explicit `owl:equivalentClass` or `owl:equivalentProperty` is stronger evidence than `rdfs:seeAlso`. The latter helps identify a candidate but does not assert equivalence. Local renames were checked against definitions and comments. RDFS domain/range statements imply types; they are not validation constraints. Conflicting declarations below therefore identify both semantic risks and decisions needed before a migration validation profile can be written.

## Rules for Naming and labels

| Source construct | Target convention | Example |
| --- | --- | --- |
| Class | Singular `PascalCase` | `ha:DigitalRepresentation` |
| Direct property | Active third-person `lowerCamelCase` | `ha:creates` |
| Existing reverse property | Configured reverse name in `lowerCamelCase` | `ha:isCreatedBy` |
| Possession or part relation | Use `has…` or the configured reverse expression | `ha:hasName`, `ha:hasPart`, `ha:isPartOf` |
| Named shape or ontology | `PascalCase` | `ha:PersonShape`, `ha:PersonHasNameShape` |
| Scheme or Concept | `kebab-case` for new model terms. Preserve existing SKOS concept IRIs. | `ha:available-for-consultation` |
| Boolean property | Express what `true` affirms. Use `is…` for a state, `has…` for presence, or `can…` for a capability. | `ha:isPublic`, `ha:hasMissingAudioReels`, `ha:canBeReused` |

- Apply configured acronyms, irregular verbs, per-URI overrides, and names for existing inverse pairs. 
- Keep the source inverse axioms and create no new inverse properties. 
- Align English `rdfs:label` and `sh:name` with the configured label for remapped terms. 
- Preserve Dutch and French text, contextual names and constraints on anonymous shapes, literal lexical forms, and list order. 
- Resolve relative IRIs against the source base and keep blank-node identities scoped to each source file.
- Identify Boolean properties from `rdfs:range xsd:boolean` or `sh:datatype xsd:boolean` and flag conflicting datatype declarations. The current exporter takes property names from its naming configuration. For example, it maps `https://data.hetarchief.be/ns/description/hasMissingAudioReels` to `https://data.hetarchief.be/ns/hasMissingAudioReels` through a configured name.

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
| `haTer` | `https://data.hetarchief.be/ns/terms/` |
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
| `haObj:FragmentRepresentation` | `ha:MediaFragment` | **MAP** | O | Preserve links to the intellectual entity and source file; M04. |
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
| `ebucore:MediaFragment` | `ha:MediaFragment` | **MAP** | D | Covers spatial and temporal fragments; M04. |
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
| `schema:Collection` | `ha:Collection` | **MAP** | D | The target class is a subclass of `ha:Thing`. |
| `schema:ContactPoint` | `ha:ContactPoint` | **MAP** | G | — |
| `schema:Country` | `ha:Country` | **MAP** | G | The target class is a subclass of `ha:Place` (M12). |
| `schema:CreativeWork` | `premis:IntellectualEntity` (per resource) | **MAP** | D | - |
| `schema:CreativeWorkSeason` | `ha:Season` | **MAP** | D | — |
| `schema:CreativeWorkSeries` | `ha:Series` | **MAP** | D | — |
| `schema:Episode` | `ha:Episode` | **MAP** | D | — |
| `schema:Newspaper` | `ha:Newspaper` | **MAP** | D | — |
| `schema:PerformanceRole` | `ha:CastMemberEntry` | **MAP** | D | Preserve the cast entry and its performer link (M02). |
| `schema:Person` | `ha:Person` | **MAP** | D, E, G | — |
| `schema:Place` | `ha:Place` | **MAP** | D | — |
| `schema:PostalAddress` | `ha:PostalAddress` | **MAP** | G | — |
| `schema:QuantitativeValue` | `ha:QuantitativeValue` | **MAP** | D, O | — |
| `schema:Role` | `ha:Role` | **CHANGE** | D | Preserve role identity and move its agent link to rdf:value; M02. |
| `schema:Thing` | `ha:Thing` by default or the applicable agent class | **CHANGE** | D | Use `ha:Person`, `ha:Organization` or `ha:Agent` in agent contexts under M02. |
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
| `premis:File` | `premis:File` | **KEEP** | D, O | Add `ha:MediaFile` to files with a qualifying MIME type; M04. |
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
| `haDes:audioRecordingSpeed` | `ha:hasAudioRecordingSpeed` | **MAP** | D | Preserve all speed concept IRIs. Fix the draft vocabulary and align validation for variable speed (M05). |
| `haDes:broadcastingOrganization` | `ha:hasBroadcastingOrganization` | **MAP** | D | — |
| `haDes:chapterNumber` | `ha:hasChapterNumber` | **MAP** | D | — |
| `haDes:coloringType` | `ha:hasFilmColorType` | **MAP** | D | — |
| `haDes:executor` | `ha:hasExecutor` | **CHANGE** | D | On a work, rename; on a role, move the agent link to rdf:value; M02. |
| `haDes:hasMissingAudioReels` | `ha:hasMissingSoundReels` | **MAP** | D | Preserve xsd:boolean; the target range now agrees. |
| `haDes:hasMissingImageReels` | `ha:hasMissingImageReels` | **MAP** | D | Preserve xsd:boolean; the target range now agrees. |
| `haDes:iec60094Type` | `ha:hasIEC60094Type` | **MAP** | D | — |
| `haDes:licenseDistributor` | `ha:hasLicenseDistributor` | **CHANGE** | D | Preserve the agent link and apply M02 typing. |
| `haDes:numberOfAudioChannels` | `ha:hasNumberOfAudioChannels` | **MAP** | D | — |
| `haDes:numberOfAudioTracks` | `ha:hasNumberOfAudioTracks` | **MAP** | D | — |
| `haDes:numberOfMissingAudioReels` | `ha:hasNumberOfMissingSoundReels` | **MAP** | D | — |
| `haDes:numberOfMissingImageReels` | `ha:hasNumberOfMissingImageReels` | **MAP** | D | — |
| `haDes:numberOfPages` | `ha:hasNumberOfPages` | **MAP** | D | — |
| `haDes:numberOfReels` | `ha:hasNumberOfReels` | **MAP** | D | — |
| `haDes:owner` | `ha:hasOwner` | **CHANGE** | D | Preserve the agent link and apply M02 typing. |
| `haDes:pageNumber` | `ha:hasPageNumber` | **MAP** | D | — |

### Legacy object and Mediahaven properties

| Source term | Target term / action | Status | Used in | Notes |
| --- | --- | --- | --- | --- |
| `haObj:hasAccessCopy` | `ha:hasAccessCopy` | **MAP** | O | — |
| `haObj:hasCarrierCopy` | `ha:hasCarrierRepresentation` | **MAP** | D, O | — |
| `haObj:hasFragmentRepresentation` | `ha:hasFragmentRepresentation` | **MAP** | O | Links the intellectual entity to its `ha:MediaFragment`; M04. |
| `haObj:hasIIIFCopy` | `ha:hasIIIFCopy` | **MAP** | O | — |
| `haObj:hasMasterCopy` | `ha:hasMasterCopy` | **MAP** | O | — |
| `haObj:hasMezzanineCopy` | `ha:hasMezzanineCopy` | **MAP** | O | — |
| `haObj:hasTranscriptionCopy` | `ha:hasTranscriptionCopy` | **MAP** | O | — |
| `haObj:isAccessCopyOf` | `ha:isAccessCopyOf` | **MAP** | O | Preserve representation-to-intellectual-entity direction; current target domain/range agree; M16. |
| `haObj:isCarrierCopyOf` | `ha:isCarrierRepresentationOf` | **MAP** | O | — |
| `haObj:isFragmentRepresentationOf` | `ha:isFragmentRepresentationOf` | **MAP** | O | Links the `ha:MediaFragment` to the intellectual entity it represents; M04. |
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
| `org:identifier` | `ha:hasIdentifier` | **MAP** | G | Preserve the source string (M01). |
| `org:postIn` | `ha:isPostIn` | **MAP** | G | — |
| `org:role` | `ha:hasRoleType` | **REVIEW** | G | Preserve the role-type concept. The target domain still needs a decision for posts (M02). |
| `org:siteAddress` | `ha:hasSiteAddress` | **MAP** | G | — |
| `org:siteOf` | `ha:isSiteOf` | **MAP** | G | — |
| `org:unitOf` | `ha:isUnitOf` | **MAP** | G | — |

### Schema.org properties

| Source term | Target term / action | Status | Used in | Notes |
| --- | --- | --- | --- | --- |
| `schema:about` | `ha:isAbout` | **MAP** | D | — |
| `schema:abstract` | `ha:hasAbstract` | **MAP** | D | Preserve language tags. The target uses `ha:hasDescription` as its superproperty (M07). |
| `schema:actor` | `ha:hasCastMember` | **CHANGE** | D | Link the work to the cast entry and move the performer link to `rdf:value` (M02). |
| `schema:addressCountry` | `ha:hasAddressCountry` | **CHANGE** | G | Preserve country nodes; resolve literal countries to entities; M12. |
| `schema:addressLocality` | `ha:hasAddressLocality` | **MAP** | G | — |
| `schema:addressRegion` | `ha:hasAddressRegion` | **MAP** | G | — |
| `schema:alternateName` | `ha:hasAlternateName` | **MAP** | D | Preserve language tags; target range now agrees; M07. |
| `schema:artMedium` | `ha:hasArtMedium` | **MAP** | D | Preserve language tags; target range now agrees; M07. |
| `schema:artform` | `ha:hasArtform` | **MAP** | D | Preserve language tags; target range now agrees; M07. |
| `schema:birthDate` | `ha:hasBirthDate` | **CHANGE** | G | Validate and retype the EDTF literal while preserving its lexical form (M06). |
| `schema:birthPlace` | `ha:hasBirthPlace` | **CHANGE** | G | Target now uses `ha:Place`. Source literal must become a resolved place entity (M12). |
| `schema:brand` | `ha:hasBrand` | **MAP** | D, E | — |
| `schema:caption` | `ha:hasCaptionText` | **REVIEW** | D | Target now uses `premis:File`. The source caption is on a digital representation (M08). |
| `schema:characterName` | `ha:hasCharacterName` | **MAP** | D | — |
| `schema:collectionSize` | `ha:hasCollectionSize` | **CHANGE** | D | Require nonnegative values; retype valid integers to xsd:nonNegativeInteger. |
| `schema:contactPoint` | `ha:hasContactPoint` | **MAP** | G | — |
| `schema:contactType` | `ha:hasContactType` | **MAP** | G | — |
| `schema:containedInPlace` | `ha:isContainedInPlace` | **MAP** | D | — |
| `schema:contributor` | `ha:hasContributor` | **CHANGE** | D | On a work, rename; on a role, move the agent link to rdf:value; M02. |
| `schema:copyrightHolder` | `ha:hasRightsHolder` | **CHANGE** | D | Preserve the rights-holder link and apply M02 typing, with `ha:Agent` as the fallback. |
| `schema:copyrightNotice` | No exact target | **UNMAPPED** | D | No dedicated notice predicate as no longer relevant. Replaced by broader rights classes. |
| `schema:copyrightYear` | `ha:hasCopyrightDate` | **UNMAPPED** | D | No longer relevant. |
| `schema:creator` | `ha:hasCreator` | **REVIEW** | D, O | Rename work-to-role links and use `rdf:value` for role-to-agent links (M02). The fixity domain now fits, but its source string still needs agent resolution (M13). |
| `schema:creditText` | `ha:hasCreditText` | **MAP** | D | Preserve language tags; target range now agrees; M07. |
| `schema:dateCreated` | `ha:hasCreationDate` | **CHANGE** | D, O | Normalize to `edtf:EDTF` where lossless. Keep dates on their original subjects, including files and Mediahaven fragments (M06). |
| `schema:dateDeleted` | `ha:hasDeletionDate` | **MAP** | O | Mediahaven fragment deletion timestamp; preserve xsd:dateTime. |
| `schema:dateModified` | `ha:hasModificationDate` | **MAP** | O | Mediahaven fragment modification timestamp; preserve xsd:dateTime. |
| `schema:datePublished` | `ha:hasPublicationDate` | **CHANGE** | D | Normalize level-specific literals to `edtf:EDTF` on intellectual entities and digital representations (M06). |
| `schema:deathDate` | `ha:hasDeathDate` | **CHANGE** | G | Validate and retype the EDTF literal while preserving its lexical form (M06). |
| `schema:deathPlace` | `ha:hasDeathPlace` | **CHANGE** | G | Source literal must become a resolved place entity; M12. |
| `schema:depth` | `ha:hasDepth` | **MAP** | D | — |
| `schema:description` | `ha:hasDescription` | **MAP** | D | — |
| `schema:duration` | `ha:hasDuration` | **MAP** | D, O | — |
| `schema:email` | `ha:hasEmail` | **MAP** | G | — |
| `schema:endDate` | `ha:hasEndDate` | **MAP** | D | Preserve `xsd:dateTime` on newspapers (M06). |
| `schema:endTime` | `ha:hasEndOffset` | **CHANGE** | D, O | Convert confirmed media-relative offsets to `xsd:decimal` seconds (M04). |
| `schema:familyName` | `ha:hasFamilyName` | **MAP** | G | — |
| `schema:genre` | `ha:hasGenre` | **MAP** | D | Preserve language tags; target range now agrees; M07. |
| `schema:givenName` | `ha:hasGivenName` | **MAP** | G | — |
| `schema:hasPart` | `ha:hasPart` | **MAP** | D | — |
| `schema:height` | `ha:hasHeight` | **MAP** | D, O | Preserve measurement nodes; corrected domain union now includes files; M05. |
| `schema:identifier` | `ha:hasIdentifier` | **MAP** | D, O | Preserve the source string, including leading zeroes (M01). |
| `schema:inLanguage` | `ha:hasLanguage` | **REVIEW** | D | Validate/normalize xsd:language; representation/caption subjects exceed domain; M07. |
| `schema:instrument` | `ha:hasInstrument` | **MAP** | E | — |
| `schema:isPartOf` | `ha:isPartOf` | **REVIEW** | D | Most individual-to-collection links fit; source also uses collection subjects; M10. |
| `schema:issueNumber` | `ha:hasIssueNumber` | **MAP** | D | Preserve the exact `xsd:string` designation. Check publication-issue typing (M10). |
| `schema:keywords` | `ha:hasKeywords` | **MAP** | D | Preserve language tags; target range now agrees; M07. |
| `schema:license` | `ha:hasReuseCondition` | **MAP** | D | — |
| `schema:locationCreated` | `ha:hasCreationPlace` | **MAP** | D | The collection domain covers newspapers. Preserve the place IRI and apply the `ha:Place` class mapping (M12). |
| `schema:logo` | `ha:hasLogo` | **MAP** | G | — |
| `schema:maintainer` | `ha:hasMaintainer` | **MAP** | D | — |
| `schema:material` | `ha:hasMaterial` | **MAP** | D | — |
| `schema:materialExtent` | `ha:hasMaterialExtent` | **MAP** | D | — |
| `schema:mentions` | `ha:mentions` | **MAP** | D | — |
| `schema:model` | `ha:hasModel` | **MAP** | E | Preserve `xsd:string` values on hardware and software agents (M13). |
| `schema:name` | `ha:hasName` | **CHANGE** | D, E, G | Preserve language-tagged names. Tag plain-string country names with `nl` (M07). |
| `schema:position` | `ha:hasPosition` | **MAP** | D | Preserve `xsd:integer`. The collection domain covers the mapped series (M10). |
| `schema:postOfficeBoxNumber` | `ha:hasPostOfficeBoxNumber` | **MAP** | G | — |
| `schema:postalCode` | `ha:hasPostalCode` | **MAP** | G | — |
| `schema:producer` | `ha:hasProducer` | **CHANGE** | D | Rename work links and move role-to-agent links to `rdf:value` (M02). |
| `schema:publisher` | `ha:hasPublisher` | **CHANGE** | D | Rename intellectual-entity links and move role-to-agent links to `rdf:value`. Review newspaper-series subjects (M02). |
| `schema:roleName` | `ha:hasRoleType` | **MAP** | D | Preserve `xsd:string` names and concept IRIs. Apply the `ha:RoleType` class mapping to concepts (M02). |
| `schema:seasonNumber` | `ha:hasSeasonNumber` | **MAP** | D | Preserve `xsd:integer` on the mapped `ha:Season` (M10). |
| `schema:serialNumber` | `ha:hasSerialNumber` | **MAP** | E | Preserve the string under the dedicated serial-number predicate (M01). |
| `schema:spatial` | `ha:hasSpatial` | **MAP** | D | Keep the place IRI and apply the `ha:Place` class mapping (M12). |
| `schema:startDate` | `ha:hasStartDate` | **MAP** | D | Preserve `xsd:dateTime` on newspapers (M06). |
| `schema:startTime` | `ha:hasStartOffset` | **CHANGE** | D, O | Convert confirmed media-relative offsets to `xsd:decimal` seconds (M04). |
| `schema:streetAddress` | `ha:hasStreetAddress` | **MAP** | G | — |
| `schema:telephone` | `ha:hasTelephone` | **MAP** | G | — |
| `schema:temporal` | `ha:hasTemporal` | **MAP** | D | Preserve language tags. The coverage superproperty now accommodates `rdf:langString` (M07). |
| `schema:thumbnailUrl` | `ha:hasThumbnailURL` | **CHANGE** | D | Source IRI becomes an xsd:anyURI literal if following the declared range; M07. |
| `schema:transcript` | `ha:hasTranscript` | **MAP** | D | Preserve the `xsd:string` on its digital representation (M08). |
| `schema:unitCode` | `ha:hasUnitCode` | **MAP** | D | — |
| `schema:unitText` | `ha:hasUnitText` | **MAP** | D | — |
| `schema:value` | `ha:hasMeasurementValue` | **MAP** | D | Only quantitative measurements map here; keep xsd:float; M05. |
| `schema:vatID` | `ha:hasVATID` | **MAP** | G | — |
| `schema:version` | `ha:hasVersion` | **MAP** | E | — |
| `schema:width` | `ha:hasWidth` | **MAP** | D, O | Preserve measurement nodes; corrected domain union now includes files; M05. |

### Dublin Core, BIBFRAME and FOAF properties

| Source term | Target term / action | Status | Used in | Notes |
| --- | --- | --- | --- | --- |
| `bf:edition` | `ha:hasEdition` | **MAP** | D | Preserve the concept IRI. Check publication-issue typing (M10/M11). |
| `bf:issuance` | `ha:hasIssuance` | **CHANGE** | D | Preserve frequency concept IRIs. Align the range class and validation before applying its type (M10/M11). |
| `bf:precededBy` | `ha:isPrecededBy` | **MAP** | D | Preserve the newspaper-to-newspaper link and its direction (M10). |
| `bf:productionMethod` | `ha:hasProductionMethod` | **MAP** | D | Preserve the concept IRI. The vocabulary supplies the required `ha:ProductionMethod` type (M11). |
| `bf:succeededBy` | `ha:isSucceededBy` | **MAP** | D | — |
| `bf:supplement` | `ha:hasSupplement` | **MAP** | D | — |
| `bf:supplementTo` | `ha:isSupplementTo` | **MAP** | D | — |
| `dct:available` | `ha:hasAvailabilityDate` | **CHANGE** | D | Convert `xsd:dateTime` to `edtf:EDTF` where time and offset can be preserved (M06). |
| `dct:description` | `ha:hasDescription` | **MAP** | G | — |
| `dct:format` | `ha:hasFormat` on files; class derivation on intellectual entities | **REVIEW** | D, O | File-format links now map directly; intellectual-entity strings still need classification; M03. |
| `dct:license` | `ha:hasReuseCondition` | **REVIEW** | R | Digital-representation usage conflicts with target domain; M17. |
| `dct:rights` | `ha:hasRightsStatement` (statement IRIs) | **MAP** | D, R | Preserve both values when present. See M14/M17. |
| `foaf:homepage` | `ha:hasHomepage` | **CHANGE** | G | Source IRI becomes an xsd:anyURI literal if following the declared range; M07. |

### EBUCore, ordering and preservation relationship properties

| Source term | Target term / action | Status | Used in | Notes |
| --- | --- | --- | --- | --- |
| `ebucore:annotationConfidence` | `ha:hasAnnotationConfidence` | **MAP** | D | — |
| `ebucore:annotationType` | `ha:hasAnnotationType` | **CHANGE** | D | Keep concept IRI; type the selected concept as ha:AnnotationType; M09. |
| `ebucore:hasAnnotationRelatedAgent` | `ha:hasAnnotationSubject` | **CHANGE** | D | Merge subject links while recording their original predicates; M09. |
| `ebucore:hasAnnotationRelatedArtefact` | `ha:hasAnnotationSubject` | **CHANGE** | D | Merge subject links while recording their original predicates; M09. |
| `ebucore:hasAnnotationTarget` | `ha:hasAnnotationTarget` | **MAP** | D | — |
| `ebucore:hasCaptioning` | `ha:hasSubtitling` | **MAP** | D | File/image-reel domains now fit; classify caption objects by purpose; M08. |
| `ebucore:hasCastMember` | `ha:hasCastMember` | **CHANGE** | D | Source string should be parsed and transformed into structured cast entries; M02. |
| `ebucore:hasMediaFragment` | `ha:hasMediaFragment` | **CHANGE** | D, O | Preserve direction and type the source file as `ha:MediaFile` once its MIME type qualifies; M04. |
| `ebucore:hasMimeType` | `ha:hasMimeType` | **MAP** | O | Preserve strings and use them to identify eligible media files; M03/M04. |
| `ebucore:hasObjectType` | `ha:hasObjectType` | **MAP** | D | — |
| `ebucore:height` | `ha:hasHeight` | **MAP** | D | Integer literal becomes a measurement node; unit depends on class context; M05. |
| `ebucore:isAnnotatedMediaResource` | `ha:annotatesMediaResource` | **MAP** | D | Preserve the annotation-to-fragment direction; the target also accepts `ha:MediaFile`; M04/M09. |
| `ebucore:isMediaFragmentOf` | `ha:isMediaFragmentOf` | **CHANGE** | D, O | Preserve direction and type the linked file as `ha:MediaFile` once its MIME type qualifies; M04. |
| `ebucore:regionDelimX` | `ha:hasRegionX` | **CHANGE** | D | Validate nonnegative pixel coordinates; reject negative or unknown-unit values; M05. |
| `ebucore:regionDelimY` | `ha:hasRegionY` | **CHANGE** | D | Corrected seeAlso now matches; validate nonnegative pixel coordinates as for X; M05. |
| `ebucore:synopsis` | `ha:hasSynopsis` | **MAP** | D | - |
| `ebucore:width` | `ha:hasWidth` | **MAP** | D | Integer literal becomes a measurement node; unit depends on class context; M05. |
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
| `premis:identifier` | `ha:hasLocalIdentifier` for local identifier nodes | **MAP** | O | Preserve the existing nodes. Keep `premis:identifier` for other PREMIS identifier usages (M01). |
| `premis:medium` | `premis:medium` | **KEEP** | O | Preserve the external predicate. |
| `premis:note` | `premis:note` | **KEEP** | E, R | Preserve the external predicate. |
| `premis:originalName` | `premis:originalName` | **KEEP** | O | Preserve the external predicate. |
| `premis:outcome` | `premis:outcome` | **KEEP** | E | Preserve the predicate and map its three outcome values. |
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
| `skos:altLabel` | `ha:hasAlternateName` on organizations | **MAP** | G | Context-specific name mapping; preserve language tags and keep SKOS labels on concepts; M07. |
| `skos:prefLabel` | `ha:hasName` on organizations; `skos:prefLabel` on concepts | **MAP** | G | Preserve language tags; role-type concept labels stay SKOS; M02/M07. |

## Decisions and transformation rules

The following model changes resolve migration findings. The REVIEW and UNMAPPED contexts below identify decisions still needed for the affected rules.

| Resolved finding | Effect on the plan |
| --- | --- |
| The model distinguishes `ha:hasIdentifier`, `ha:hasLocalIdentifier` and `ha:hasPrimaryLocalIdentifier`. | Keep identifier strings and reuse existing local identifier nodes and primary selections (M01). |
| `ha:hasCastMember` ranges over `ha:CastMemberEntry`. | Apply the work → cast entry → performer transformation in M02. |
| `ha:hasCreator`, `ha:hasContributor`, `ha:hasPublisher` and `ha:hasProducer` accept `ha:Agent` or `ha:Role`. | Preserve contextual roles and use `ha:Agent` for existing agents whose specific type is unknown (M02). |
| `ha:hasRoleType` accepts `ha:RoleType` resources and `xsd:string`. | Preserve both forms of legacy role names. Organizational posts still need a domain decision (M02). |
| `ha:hasFormat` now ranges over `ha:FileFormat`, and MIME type no longer inherits that range. | File-format links and MIME strings can migrate directly; intellectual-entity format classifications remain contextual (M03). |
| `ha:hasStartOffset` and `ha:hasEndOffset` range over `xsd:decimal`. | Preserve fractional seconds when converting media-relative offsets and align SHACL with the decimal range (M04). |
| Width/height domains now include `premis:File`, and height uses `owl:unionOf`. | Existing measurement-node links can migrate directly; literal dimensions still require known units (M05). |
| `ha:hasRegionY` now references `ebucore:regionDelimY`. | Apply the same nonnegative-pixel conversion as for X (M05). |
| `ha:hasMeasurementValue` is a one-way subproperty of `rdf:value`. | No reverse measurement inference is declared; retain context-specific conversions (M05). |
| Creation, publication, availability, birth and death dates range over `edtf:EDTF`. Creation dates cover files and Mediahaven fragments, and publication dates cover digital representations. | Keep dates on their original subjects and preserve precision and uncertainty during datatype normalization (M06). |
| The nine text properties in M07 range over `rdf:langString`. `ha:hasAbstract` uses `ha:hasDescription` as its superproperty, and `ha:hasCoverage` accepts language-tagged text and resources. | Preserve language tags on descriptive text and temporal coverage, and keep spatial coverage IRIs. Tag plain-string country names with `nl`. Synopsis typing and the imported PREMIS note still need attention (M07/M12). |
| Captioning and subtitling domains now include files and image reels. | The subject-domain blocker is resolved; caption purpose and object classification remain open (M08). |
| `ha:hasCaptionText` now uses the declared class `premis:File`. | The undefined class reference is resolved. Caption text on digital representations still needs a domain decision (M08). |
| `ha:hasTranscript` now has domain `ha:DigitalRepresentation`. | Keep transcript text on the representation that carries it (M08). |
| `ha:hasPosition` now includes collections in its domain, and `ha:hasEdition` accepts concept objects. | Preserve series positions and edition concept IRIs. The newspaper-issue hierarchy still needs a decision for validation (M10/M11). |
| `ha:hasIssueNumber` is a string identifier, and `ha:isPrecededBy` links newspapers. | Preserve issue designations verbatim and keep predecessors at the newspaper-series level (M10). |
| `ha:hasIssuance` now describes frequency. | Preserve legacy frequency concepts and align the definition and validation of `ha:Issuance` (M11). |
| `ha:hasProductionMethod` ranges over `ha:ProductionMethod`, and the three vocabulary entries have that type. | Keep production-method concept IRIs on their carrier representations (M11). |
| `ha:hasBirthPlace` ranges over `ha:Place`, and `ha:hasCreationPlace` covers collections and intellectual entities. | Preserve the creation-place links on newspapers. Birth and death place strings still need resolution (M12). |
| `ha:hasModel` has a domain covering hardware and software, and `ha:hasCreator` includes `premis:Fixity`. | Preserve model strings on both agent types. Fixity creator strings still require agent resolution (M13). |
| The inverse access-copy domain/range agree with source direction. | Preserve representation → intellectual entity edges (M16). |
| `ha:metadataScope` and `ha:contentScope` are declared left operands and appear in the target allowed list. `ha:extended` and `ha:limited` have type `ha:MetadataScope`. | Rewrite operands in instance data and reusable permissions. Correct the target right-operand class check before validation (M17). |
| `ha:fail`, `ha:success` and `ha:warning` have type `premis:OutcomeStatus`. | Map the event outcome IRIs directly and align the draft SHACL allowed list. |

### M01 — Separate literal identifiers, local identifier nodes and primary identifiers

The target defines distinct properties for the three source patterns. The domain of `ha:hasIdentifier` includes `premis:Object`, `ha:Thing` and `ha:Collection`. `ha:hasLocalIdentifier` covers `premis:Object` and `ha:Thing`, including collections through their superclass. `ha:hasPrimaryLocalIdentifier` has domain `premis:Object` (`hetarchief/model.rdfs.ttl:1460` and `hetarchief/model.rdfs.ttl:2485`).

- Map string-valued `schema:identifier` and `org:identifier` to `ha:hasIdentifier`. Preserve the exact strings, including leading zeroes. **REVIEW** identifier-domain coverage for `ha:MediahavenFragment` and `ha:MediahavenRecord`, which have no declared superclass in that domain. Map serial numbers to `ha:hasSerialNumber`, which has the same `xsd:string` range as its superproperty `ha:hasIdentifier`.
- Map `premis:identifier` links from intellectual entities to existing `haObj:LocalIdentifier` nodes to `ha:hasLocalIdentifier`. Retype the nodes to `ha:LocalIdentifier` and keep their identities and `rdf:value` strings. Retain `premis:identifier` links outside this local-identifier context.
- Map `haObj:primaryIdentifier` to `ha:hasPrimaryLocalIdentifier` and preserve the explicitly selected node. Keep both links when the source includes a local identifier link and a primary selection for the same node.

Both object-valued target properties are subproperties of `premis:identifier`. For consumers that query explicit triples, update the query paths or materialize the PREMIS superproperty links. Preserve identifiers independently when their strings match across systems. Keep `rdf:value` on checksums and storage locations as well (M05).

### M02 — Preserve contribution roles and distinguish role assignments from role types

The source repeats contribution predicates on two levels: `work → role → agent` (`description/description.shacl.ttl:140` and `description/description.shacl.ttl:1837`). A global predicate replacement would make the role node another work or intellectual entity through the target domains.

For a contextual contribution:

1. Preserve the existing role node's identity and map its class to `ha:Role`, using `ha:CastMemberEntry` for cast credits.
2. Rename the incoming work predicate to `ha:hasCreator`, `ha:hasContributor`, `ha:hasPublisher`, `ha:hasProducer`, `ha:hasCastMember` or `ha:hasExecutor`, as appropriate.
3. Replace the role's outgoing `schema:creator`, `schema:contributor`, `schema:publisher`, `schema:producer`, `schema:actor` or `haDes:executor` agent link with `rdf:value`. The `ha:Role` restriction calls for an `rdf:value` pointing to an `ha:Agent` (`hetarchief/model.rdfs.ttl:560`).
4. Preserve `schema:characterName` as `ha:hasCharacterName`. Map `schema:roleName` to `ha:hasRoleType` and preserve both `xsd:string` literals and concept IRIs. Retype `haDes:RoleName` concepts as `ha:RoleType` (`hetarchief/model.rdfs.ttl:1542`).

The creator assignment below illustrates the fallback for a resource whose specific agent type is unknown.

```turtle
# Before
:work schema:creator :credit .
:credit a schema:Role ;
    schema:creator :creator ;
    schema:roleName :director .
:creator a schema:Thing .

# After
:work ha:hasCreator :credit .
:credit a ha:Role ;
    rdf:value :creator ;
    ha:hasRoleType :director .
:creator a ha:Agent .
:director a ha:RoleType .
```

In an agent position, preserve the existing resource and link. Use `ha:Person` or `ha:Organization` when source evidence supports the classification. Otherwise give the generic `schema:Thing` resource an explicit `rdf:type ha:Agent`. Apply this rule to role agents, including cast performers and executors, as well as rights holders, owners and license distributors. Generic resources outside agent contexts map to `ha:Thing`.

`ha:hasCreator`, `ha:hasContributor`, `ha:hasPublisher` and `ha:hasProducer` accept a direct `ha:Agent` where the source already has a direct agent link and the subject fits the domain. `ha:hasExecutor` accepts `ha:Person`, `ha:Organization` or `ha:Role`. Keep the role wrapper for executor credits with a generic agent. **REVIEW** `schema:publisher` on newspaper series because `ha:hasPublisher` has domain `premis:IntellectualEntity`, while `ha:Newspaper` belongs to the collection hierarchy.

Map the `schema:actor` work-to-role link to `ha:hasCastMember` and type the role as `ha:CastMemberEntry`. Preserve cast order as `ha:hasPosition`, the character name as `ha:hasCharacterName`, and the performer link as `rdf:value`. Parse `ebucore:hasCastMember` strings into structured cast entries where the text supports the conversion. Preserve the original text in provenance and record a review exception for ambiguous entries.

Use the draft cast check on `rdf:value` as the pattern for role assignments. Update `ha:hasCopyrightHolder` to `ha:hasRightsHolder` and use `ha:Agent` for rights-holder, owner and license-distributor checks.

For organizational functions, `org:Role` means an abstract SKOS concept (`ontologies/org.rdfs.ttl:45`). Preserve concept IRIs and `skos:prefLabel` when mapping them to `ha:RoleType`. **REVIEW:** `org:role` links a post to that concept, while `ha:hasRoleType` has domain `ha:Role`. The post hierarchy uses `rdf:subClassOf` (`hetarchief/model.rdfs.ttl:483`). Confirm how the property should apply to posts, including vacant posts, given the `ha:Role` agent restriction.

### M03 — Split the two uses of dct:format

On files, source `dct:format` points to a `dct:FileFormat` resource. Preserve its IRI and retype it to `ha:FileFormat`, which the model declares equivalent to `dct:FileFormat`. Map the predicate directly to `ha:hasFormat`, whose range is now `ha:FileFormat` (`hetarchief/model.rdfs.ttl:2495`).

On intellectual entities, `dct:format` is one of nine strings (`description/description.shacl.ttl:464`). These are content classifications, not file-format entities. The following are candidate class derivations, not blanket replacements of the format value:

| Source string | Candidate target treatment | Confidence / limitation |
| --- | --- | --- |
| `audio` | Add `rdf:type ha:Audio` | Clear content-class candidate. |
| `video` | Add `rdf:type ha:Video` | Clear content-class candidate. |
| `film` | Add `rdf:type ha:Film` | Clear content-class candidate. |
| `image` | Add `rdf:type ha:Image` | Clear content-class candidate. |
| `paper` | Add `ha:NewspaperIssue` | beware: paper material does not by itself establish NewspaperIssue semantics. |
| `newspaper` | Add `ha:NewspaperIssue` | Beware: distinguish an individual issue from the newspaper series. |
| `newspaperpage` | Add `rdf:type ha:NewspaperIssuePage` | Strong candidate; check parent-issue links. |
| `videofragment` | Classify the intellectual content and model its fragment representation separately | **REVIEW:** no dedicated target video-fragment intellectual-entity class. |
| `audiofragment` | Classify the intellectual content and model its fragment representation separately | **REVIEW:** no dedicated target audio-fragment intellectual-entity class. |

Keep the original classification in the migration provenance until its disposition is approved. Do not replace these strings with `ha:FileFormat` instances or turn an intellectual entity into a representation solely because its format says “fragment”.

Map `ebucore:hasMimeType → ha:hasMimeType` directly and preserve its string values. The target no longer makes this a subproperty of `ha:hasFormat`, so MIME strings no longer inherit the file-format class range.

### M04 — Migrate media files and fragments and convert fragment offsets

Map `haObj:FragmentRepresentation` and `ebucore:MediaFragment` to `ha:MediaFragment`, preserving instance IRIs. Apply the same type replacement to any records already migrated as `ha:FragmentRepresentation`. Keep `ha:isFragmentRepresentationOf` and `ha:hasFragmentRepresentation` where present to express which `premis:IntellectualEntity` the fragment represents. A fragment may describe a spatial region, a temporal segment, or both. Base any `ha:DigitalRepresentation` type on independent evidence.

Add an explicit `rdf:type ha:MediaFile` to each `premis:File` with a `ha:hasMimeType` string beginning with `audio/`, `video/` or `image/` and a nonempty subtype. For previously migrated records, replace `ha:MediaResource` with `ha:MediaFile` on qualifying files and with `ha:MediaFragment` on identified fragments. Flag unresolved resource types and files with missing or nonqualifying MIME values when a media file is required, and retain the source statements in migration provenance.

Preserve the direction of both source-file links. `ha:hasMediaFragment` goes from the media file to the fragment, and `ha:isMediaFragmentOf` goes from the fragment to the media file. `ha:annotatesMediaResource` goes from the annotation to a `ha:MediaFile` or `ha:MediaFragment` (M09).

The source uses `schema:startTime` and `schema:endTime` as `xsd:time` on both legacy fragment classes. Map them to `ha:hasStartOffset` and `ha:hasEndOffset` as **`xsd:decimal` seconds relative to the start of the source media**. Change both offset datatype checks in the draft target shape from `xsd:integer` to `xsd:decimal`. Spatial fragments can omit offsets.

Once the source values are confirmed to be relative offsets, calculate `3600 × HH + 60 × MM + SS` with decimal arithmetic. For example, `00:01:30.125` becomes `"90.125"^^xsd:decimal` and `00:01:30` becomes `"90.0"^^xsd:decimal`. **REVIEW** time-zone-bearing, wall-clock and wrapped values wherever the elapsed time cannot be established. Keep `schema:duration → ha:hasDuration` as `xsd:duration`.

### M05 — Preserve measurement structure and units

Existing `schema:QuantitativeValue` nodes become `ha:QuantitativeValue`. Map `schema:value` to `ha:hasMeasurementValue`, and rename the unit predicates to `ha:hasUnitCode` and `ha:hasUnitText`. Keep unit codes and numeric precision; do not recalculate measurements merely to rename predicates.

`ebucore:width` and `ebucore:height` are integer literals on source media fragments. Their target properties expect measurement nodes. **REVIEW:** create a measurement node only when its unit is known from the data or authoritative context; the source descriptions allow pixels or physical dimensions. The new node must preserve the original value and use the approved unit. Source file-level width/height links already point to measurement nodes and need no such wrapping.

The target width/height domain unions now include `premis:File`, and `ha:hasHeight` uses the corrected `owl:unionOf` (`hetarchief/model.rdfs.ttl:1139` and `hetarchief/model.rdfs.ttl:1739`). These declaration blockers are resolved: existing source file-level measurement-node links can migrate directly.

For region coordinates, validate that values are nonnegative and measured in pixels before emitting `ha:hasRegionX` / `ha:hasRegionY`. The Y property's corrected `seeAlso` now points to the actual source `ebucore:regionDelimY`; both coordinates use the same conversion checks.

For audio speed, preserve existing `/id/rotational-speed/` IRIs under `ha:hasAudioRecordingSpeed`. The target vocabulary types the ten numeric concepts as `ha:QuantitativeValue` and carries their existing float values and units under `ha:hasMeasurementValue`, `ha:hasUnitCode` and `ha:hasUnitText`. The draft `variable` entry assigns `ha:QuantitativeValue` and RPM units without a numeric measurement. Correct its duplicated `a` before loading the vocabulary. Align the draft quantitative-value shape with the current unit paths and allow `variable` to omit `ha:hasMeasurementValue` while requiring it for numeric speeds.

Finally, `ha:hasMeasurementValue` is declared `rdfs:subPropertyOf rdf:value`, without a global equivalence (`hetarchief/model.rdfs.ttl:1600`). This permits measurement values to entail generic RDF values without turning unrelated RDF values into measurements. Keep `rdf:value` on identifiers, checksums, storage locations and role-agent links; map only quantitative-value contexts to `ha:hasMeasurementValue`.

### M06 — Preserve date precision

| Source usage | Target | Required treatment |
| --- | --- | --- |
| `schema:dateCreated` with EDTF levels 0/1/2 or `xsd:dateTime` | `ha:hasCreationDate` with `edtf:EDTF` | Normalize valid EDTF literals and convert timestamps where lossless on intellectual entities, digital representations, files and Mediahaven fragments. |
| `schema:datePublished` with EDTF levels 0/1/2 | `ha:hasPublicationDate` with `edtf:EDTF` | Normalize valid EDTF literals on intellectual entities and digital representations. |
| `schema:copyrightYear`: integer | `ha:hasCopyrightDate`: `xsd:dateTime` | **REVIEW:** a year does not identify a day or time. A model change or a separate year representation is required. |
| `dct:available` with `xsd:dateTime` | `ha:hasAvailabilityDate` with `edtf:EDTF` | Convert where lossless and retain the original timestamp for review if the accepted format cannot express its time, fractional precision or offset. |
| `schema:birthDate` and `schema:deathDate` with EDTF level 1 | `ha:hasBirthDate` and `ha:hasDeathDate` with `edtf:EDTF` | Retype valid literals and preserve their lexical form and date uncertainty. |
| `schema:startDate`, `schema:endDate` on newspapers | `ha:hasStartDate`, `ha:hasEndDate`: `xsd:dateTime` | Rename and preserve the literal. |
| Mediahaven `schema:dateDeleted`, `schema:dateModified` | `ha:hasDeletionDate`, `ha:hasModificationDate`: `xsd:dateTime` | Rename and preserve the timestamp. |
| Rights `premis:startDate`, `premis:endDate` | Same predicates | Keep the source `xsd:dateTime` literals. |

The common `edtf:EDTF` range removes the old level-1 restriction and the need to turn descriptive creation dates into timestamps. Validate the source lexical form against the accepted EDTF profile before changing the datatype IRI. Preserve valid partial dates, intervals and uncertainty. For timestamps, require a lossless representation of the original precision and offset. See the timestamp examples in the [Library of Congress EDTF specification](https://www.loc.gov/standards/datetime/edtf.html).

Keep each date on its original subject. The draft target shapes still check level-specific EDTF datatype IRIs and use `xsd:dateTime` for availability and some creation dates. Align those checks with `edtf:EDTF` before validating migrated dates. See `description/description.shacl.ttl:107`, `objects/objects.shacl.ttl:1125` and `hetarchief/model.shacl.ttl:1094`.

### M07 — Preserve multilingual text, language codes and URI node kinds

Most source `schema:name` values, organization `skos:prefLabel` / `skos:altLabel`, and descriptive fields are `rdf:langString`. The target ranges for `ha:hasName`, `ha:hasAlternateName`, `ha:hasAbstract`, `ha:hasGenre`, `ha:hasKeywords`, `ha:hasTemporal`, `ha:hasArtform`, `ha:hasArtMedium` and `ha:hasCreditText` are now `rdf:langString`, matching `ha:hasDescription`. Preserve all language tags during direct predicate mappings. The former direct-range conflicts are resolved; the remaining exceptions are described below.

For organization labels, map `skos:prefLabel` to `ha:hasName` and `skos:altLabel` to `ha:hasAlternateName` in that context, preserving every language-tagged value. This follows their naming function and compatible target ranges; the target does not assert a global equivalence with the SKOS predicates. Keep SKOS labels on concepts, especially `ha:RoleType`, rather than renaming all occurrences globally.

Preserve the lexical form of each plain-string country name and add the default language tag `nl` when mapping it to `ha:hasName`. Preserve any existing language tag. Align `ha:CountryShape` with `rdf:langString` before validating the converted names. Review other untagged names separately.

Map temporal coverage directly and preserve its language tags. `ha:hasCoverage` now has a range of `rdf:langString` or `ha:Thing`, which also accommodates spatial coverage resources (M12).

**REVIEW** remains for `ha:hasSynopsis`, which ranges over `xsd:string` while its superproperty `ha:hasDescription` ranges over `rdf:langString`. `ha:hasAbstract` now uses only `ha:hasDescription` as its superproperty. The imported `premis:note` still references the undefined `ha:description`.

`schema:inLanguage` strings become `ha:hasLanguage` with `xsd:language`; validate the lexical form and normalize only with evidence. The target domain is an intellectual entity, while source usage also covers digital representations and open captions. Resolve that domain mismatch.

Source `foaf:homepage` and `schema:thumbnailUrl` values are IRIs, while their target ranges are `xsd:anyURI`. If the target's literal representation is retained, convert the exact IRI string to an `xsd:anyURI` literal and update consumers accordingly. If links should remain RDF resources, the target ranges need adjustment instead. Do not silently mix the two representations.

### M08 — Distinguish captioning, subtitles, caption text and transcripts

The source uses `ebucore:hasCaptioning` for files and image reels, allowing a file or closed-caption object in the former case and open captions in the latter. The target separates accessibility captions (`ha:Captioning`, `ha:ClosedCaptions`, `ha:OpenCaptions`) from general subtitles (`ha:Subtitling`, `ha:ClosedSubtitling`, `ha:OpenSubtitling`). Its comments explicitly leave the replacement question open (`hetarchief/model.rdfs.ttl:126`).

**REVIEW:** classify each existing caption object by actual purpose; do not assume all subtitles are accessibility captions. Choose the matching `ha:hasCaptioning` or `ha:hasSubtitling` link. A detached subtitle file can be `ha:ClosedSubtitling` only when its role is established. Both link properties now have domain unions covering `premis:File` and `ha:ImageReel`, resolving the image-reel subject mismatch. An otherwise unclassified file object still needs a justified captioning/subtitling type.

Map `schema:transcript` directly to `ha:hasTranscript`. Its domain is now `ha:DigitalRepresentation`, so the source `xsd:string` stays on the same representation.

**REVIEW:** the domain of `ha:hasCaptionText` is now `premis:File` (`hetarchief/model.rdfs.ttl:895`), while `schema:caption` describes a digital representation (`description/description.shacl.ttl:834`). Preserve the caption on the legacy representation until the target can express representation-level caption text or there is evidence that it applies to a specific file.

### M09 — Merge annotation subjects while retaining provenance

Map both `ebucore:hasAnnotationRelatedArtefact` and `ebucore:hasAnnotationRelatedAgent` to `ha:hasAnnotationSubject`, keeping the referenced resource IRIs. The source permits one artefact and an additional agent; retain both when they differ. When both old predicates have the same object, RDF deduplication will leave one target triple. Record the original predicates in migration provenance if their distinction is needed.

Retype only concepts actually used as `ebucore:annotationType` values to `ha:AnnotationType`. Preserve `ebucore:annotationConfidence → ha:hasAnnotationConfidence` as a decimal. Map `ebucore:isAnnotatedMediaResource` to `ha:annotatesMediaResource`, keeping the annotation as the subject and the annotated fragment or qualifying media file as the object (M04). Preserve the separate target file link as `ha:hasAnnotationTarget`.

### M10 — Keep grouping, structural membership and publication sequencing distinct

`schema:CreativeWork` appears as a permitted value class but has no single corresponding generic class in the target. Existing explicit series, season, collection, archive-component and newspaper types have the tabled destinations. **REVIEW:** a resource known only as `schema:CreativeWork` must be classified as a grouping or an individual intellectual work before a replacement class is chosen.

Keep the source distinction between generic `schema:hasPart` / `schema:isPartOf` and PREMIS structural relationships `rel:hsp` / `rel:isp`. They map to `ha:hasPart` / `ha:isPartOf` and `ha:hasStructuralPart` / `ha:isStructuralPartOf`, respectively. Cross-category preservation inclusion uses `ha:includes` / `ha:isIncludedIn`. Do not collapse these relationships.

The `ha:hasPosition` domain now includes `ha:Collection`, which covers the mapped `ha:Series` subjects. Map their integer positions directly. Map integer season numbers directly to `ha:hasSeasonNumber` on `ha:Season`. **REVIEW** remains for `ha:isPartOf`, whose domain only covers intellectual entities while source series, seasons and archive components also use it. Resolve how to represent membership on those collections.

Map `bf:precededBy` directly to `ha:isPrecededBy`. Its domain and range are both `ha:Newspaper`, matching the draft SHACL constraint and the source context. The subject is the later newspaper and the object is its predecessor. The target mappings for `bf:succeededBy`, `bf:supplement` and `bf:supplementTo` likewise preserve newspaper-to-newspaper links.

Map `schema:issueNumber` directly to `ha:hasIssueNumber`. Its range is `xsd:string` and its superproperty is `ha:hasIdentifier`. Preserve the exact issue designation, including leading zeroes and alphanumeric characters. **REVIEW** the hierarchy or explicit dual typing before validation. `ha:NewspaperIssue` has no declared subclass link to `ha:PublicationIssue`, which is the domain for issuance, edition and issue number.

For `edm:isNextInSequence → ha:immediatelyFollows`, preserve direction: **the subject follows the object**. This agrees with the legacy EDM definition (`ontologies/edm.rdfs.ttl:12`); do not reverse the edge based on the English name alone.

### M11 — Resolve production method, edition and issuance semantics

Map `bf:productionMethod` to `ha:hasProductionMethod` on carrier representations. Keep the existing `handwritten`, `typed` and `printed` concept IRIs. `hetarchief/terms/production-method.skos.ttl` declares all three as `ha:ProductionMethod`, matching the RDFS range. The draft shape allows these same IRIs and checks `skos:Concept`. Use `ha:ProductionMethod` for the acceptance class check.

Map `bf:edition` to `ha:hasEdition` and preserve the edition-type concept IRIs. The target retains `skos:Concept` as the range and has removed the datatype-property declaration. Apply the publication-issue typing check in M10.

Map source `bf:issuance` to `ha:hasIssuance` for publication-frequency concepts such as daily or weekly, preserving their IRIs and SKOS descriptions (`description/description.shacl.ttl:1140` and `hetarchief/model.rdfs.ttl:1162`). **REVIEW** the range class before typing those concepts. `ha:Issuance` still defines mode of issuance. Align its definition with frequency, then give the frequency concepts the `ha:Issuance` type and update the draft SHACL class check from `skos:Concept` to `ha:Issuance`. Apply the publication-issue typing check in M10.

### M12 — Resolve literal places and countries without guessing identity

Source birth and death places are strings, and address country can be a string or a `schema:Country` resource. Keep existing resource identities and apply the class mappings. `ha:Country` is a subclass of `ha:Place`. Resolve strings through an approved authority or a documented local-node policy, preserving their original text. Record ambiguous or unresolved strings as exceptions.

Birth, death and creation places share the `ha:Place` range. Map `schema:spatial` links directly and preserve each place IRI, since `ha:Place` is a subclass of `ha:Thing` and the `ha:hasCoverage` union range includes `ha:Thing`. Map `schema:locationCreated` directly on newspapers because `ha:Newspaper` is a subclass of `ha:Series`, which is a subclass of `ha:Collection`. Update the draft newspaper shape from `ha:hasCreationLocation` to `ha:hasCreationPlace`.

Update the draft birth- and death-place checks to accept `ha:Place` resources. The address-country check already uses `ha:Country`.

### M13 — Preserve generic provenance and hardware/software agent distinctions

`prov:wasDerivedFrom` is used from intellectual entities, representations and files to `mh:Fragment` metadata records (`objects/objects.shacl.ttl:304`). That predicate is not defined in the supplied target PROV extract. `ha:hasDerivationSource` is not a safe substitute: it links preservation objects to preservation objects, while `ha:MediahavenFragment` describes the metadata-system fragment. The target itself raises the question of a generic derivation property (`hetarchief/model.rdfs.ttl:1462`). **UNMAPPED:** preserve these provenance links until the model explicitly retains/imports the PROV property or defines a suitable alternative. The Mediahaven fragment class and its record relation can migrate independently.

Keep `prov:generated` on generic `prov:Activity` instances. Only an established preservation-event-to-object link is eligible for the more specific `ha:hasOutput`; the original `evtObjRole:out` already maps there directly. Do not narrow arbitrary generated IRIs to preservation objects.

The source also uses `schema:creator` as a string on `premis:Fixity` (`objects/objects.shacl.ttl:1003`). `ha:hasCreator` includes fixity subjects and accepts an `ha:Agent` or `ha:Role` resource. **REVIEW** whether the literal can be resolved to a resource under an approved attribution rule. Apply M02 typing to the resolved agent. Keep the original value in the legacy graph when agent resolution is unavailable.

Map `schema:model` directly to `ha:hasModel` for both hardware and software agents. Its `xsd:string` range and union domain match the shared source model property (`hetarchief/model.rdfs.ttl:1303` and `events/events.shacl.ttl:282`).

### M14 — Preserve copyright notices separately from general rights text

No dedicated target equivalent of `schema:copyrightNotice` was identified. Combining notices with general source `dct:rights` text loses the distinction. **UNMAPPED:** preserve notices under their original predicate pending a decision to keep an external notice term, add a dedicated target term, or explicitly accept a broader mapping with provenance.

Keep language-tagged text under `dct:rights` in D and map rights-statement IRIs to `ha:hasRightsStatement` in R. Preserve both values when both exist.

### M15 — Review request-form links versus templates

`haOrg:requestForm` describes a string containing the URL of a request form. `ha:hasContentRequestFormTemplate` explicitly describes a URI template whose placeholders are replaced with content-specific values. **REVIEW:** a plain URL may be usable as a constant template, but that behavior must be confirmed in the application. Preserve existing placeholders verbatim where present; do not invent item parameters. Evidence: `organizations/organizations.rdfs.ttl:144` and `hetarchief/model.rdfs.ttl:1542`.

### M16 — Preserve inverse access-copy direction

Map `haObj:isAccessCopyOf` directly to `ha:isAccessCopyOf`: digital representation → intellectual entity. The current workspace target declares domain `ha:DigitalRepresentation`, range `premis:IntellectualEntity`, and inverse `ha:hasAccessCopy` (`hetarchief/model.rdfs.ttl:2128`), which agree with this direction. Preserve the source edge; check its inverse against the corresponding intellectual-entity-to-representation link.

### M17 — Migrate rights values as well as predicates

Keep the ODRL graph structure: policy → permission/prohibition → action/constraint, constraint → left operand/operator/right operand, and policy → target. Apply the value crosswalk below, including occurrences in reusable permissions. If data was migrated against the previous draft, replace `ha:metadataScopeOperand` and `ha:contentScopeOperand` with `ha:metadataScope` and `ha:contentScope` in those left-operand positions.

`ha:extended` and `ha:limited` now have the declared type `ha:MetadataScope`. Map both controlled-value IRIs directly and correct `ha:MetadataRScope` to `ha:MetadataScope` in the draft `ha:ConstraintShape`. The right-operand list still includes action concepts while the class alternatives cover user groups and metadata and content scopes. **REVIEW:** settle those allowed-value and type combinations and the target ODRL extract's datatype-property declaration for IRI-valued `odrl:rightOperand`.

The source uses `copyrightStatus:pub` in `sh:class`; the target explicitly equates it with class `ha:PublicDomainStatus`. That supports a class mapping, but does not make a target class IRI a rights-status instance. **REVIEW:** distinguish existing status nodes typed with the source class from direct vocabulary-value objects. A direct public-domain value may require a status node typed `ha:PublicDomainStatus`; do not emit `premis:rightsStatus ha:PublicDomainStatus` as a shortcut.

Retype `dct:RightsStatement` resources to `ha:RightsStatement`, preserving their IRIs and SKOS data. Keep `premis:License`, `premis:RightsStatus`, `premis:basis`, `premis:note`, `premis:startDate` and `premis:endDate`. The target `premis:basis` ranges over `premis:RightsBasis`, but the supplied definitions do not connect `ha:RightsStatement` or `premis:License` to that superclass; establish an agreed hierarchy or typing policy. The target `ha:hasReuseCondition` has an intellectual-entity domain, although source `dct:license` also occurs on digital representations. Do not move a representation's license to its intellectual entity automatically.

The target makes `ha:hasReuseCondition` equivalent to `ha:hasAccessRights`; do not use that declaration as a reason to collapse license information, access policies and rights-status records during data conversion.

## Controlled-value crosswalk

The first two tables cover values from the source shapes' active `sh:in` lists. Apply their mappings in object positions and wherever the vocabulary resources are described or referenced. The supporting vocabulary table covers additional changes found in `hetarchief/terms/`.

### Rights operands, actions and event outcomes

| Source value | Target value | Status / note |
| --- | --- | --- |
| `haRig:metadataRange` | `ha:metadataScope` | MAP; `odrl:LeftOperand`. |
| `haRig:contentRange` | `ha:contentScope` | MAP; `odrl:LeftOperand`. |
| `haRig:extended` | `ha:extended` | MAP; target now types it as `ha:MetadataScope`; M17. |
| `haRig:limited` | `ha:limited` | MAP; target now types it as `ha:MetadataScope`; M17. |
| `haRig:full` | `ha:full` | MAP. |
| `haRig:partial` | `ha:partial` | MAP. |
| `haRig:available-for-consultation` | `ha:available-for-consultation` | MAP; action; review source right-operand usage separately. |
| `haRig:downloadable` | `ha:downloadable` | MAP; action; review source right-operand usage separately. |
| `haRig:between-partners` | `ha:between-partners` | MAP. |
| `haRig:educational-public` | `ha:educational-public` | MAP. |
| `haRig:intra-muros` | `ha:intra-muros` | MAP. |
| `haRig:public` | `ha:public` | MAP. |
| `haRig:research-public` | `ha:research-public` | MAP. |
| `odrl:eq` | `odrl:eq` | KEEP; imported operator. |
| `odrl:lt` | `odrl:lt` | KEEP; imported operator. |
| `odrl:recipient` | `odrl:recipient` | KEEP; imported left operand. |
| `odrl:dateTime` | `odrl:dateTime` | KEEP; imported left operand. |
| `odrl:absoluteTemporalPosition` | `odrl:absoluteTemporalPosition` | KEEP; imported left operand. |
| `evtOutcome:fai` | `ha:fail` | MAP; typed as `premis:OutcomeStatus`. |
| `evtOutcome:suc` | `ha:success` | MAP; typed as `premis:OutcomeStatus`. |
| `evtOutcome:war` | `ha:warning` | MAP; typed as `premis:OutcomeStatus`. |

The draft event shape still accepts `ha:failed`, `ha:succeeded` and `ha:warnings`. Change its `premis:outcome` allowed list and messages to use `ha:fail`, `ha:success` and `ha:warning` before validating migrated events.

### Other enumerations and stable concept identities

| Source values | Migration action | Status / note |
| --- | --- | --- |
| `https://data.hetarchief.be/id/iec60094-type/` with local names `I`, `II`, `III`, `IV` | Keep all four IRIs under `ha:hasIEC60094Type`. | KEEP; retain SKOS labels and scheme. |
| `https://data.hetarchief.be/id/rotational-speed/` with local names `variable`, `16-rpm`, `19-cm-s`, `2.375-cm-s`, `33-1-3-rpm`, `38-cm-s`, `4.75-cm-s`, `72-cm-s`, `78-rpm`, `90-rpm`, `9.5-cm-s` | Keep all eleven concept IRIs under `ha:hasAudioRecordingSpeed`. Preserve numeric measurements and the variable-speed designation. | MAP after the vocabulary syntax and draft SHACL checks are aligned (M05). |
| `"DBX"`, `"Dolby A"`, `"Dolby B"`, `"Dolby C"`, `"Dolby D"` | Keep the five string values under `ha:hasAudioNoiseReduction`. | KEEP. |
| `https://data.hetarchief.be/id/edition-type/` with local names `morning-edition`, `afternoon-edition`, `evening-edition`, `weekend-edition` | Keep all four concept IRIs under `ha:hasEdition`. | MAP (M10/M11). |
| `https://data.hetarchief.be/id/production-method/` with local names `handwritten`, `typed`, `printed` | Keep all three IRIs under `ha:hasProductionMethod` and load their `ha:ProductionMethod` types from the target vocabulary. | MAP (M11). |
| `https://data.hetarchief.be/id/color-type/` with local names `BandW`, `Color`, `Colorized`, `Composite`, `Tinted`, `Toned`, `UnknownColorType` | Keep all seven IRIs under `ha:hasFilmColorType`. | KEEP. |
| The nine `dct:format` strings | Use the context-specific treatment in M03. | REVIEW; do not turn them into file-format IRIs. |

### Supporting vocabularies in `hetarchief/terms/`

Load the target SKOS files for migration and validation. They preserve concept and scheme IRIs, labels, definitions and scheme memberships. Apply the following changes to any copies of the legacy vocabulary descriptions in the migrated graph.

| Target file | Changes to legacy vocabulary descriptions |
| --- | --- |
| `description-roles.skos.ttl`, `organization-roles.skos.ttl` | Replace `haDes:RoleName` and `org:Role` types with `ha:RoleType` (M02). |
| `formats.skos.ttl` | Replace `dct:FileFormat` with `ha:FileFormat` and `https://www.ebu.ch/metadata/ontologies/ebucore/ebucore#hasMimeType` with `ha:hasMimeType`. Map `haTer:higherPriority` to `ha:hasLowerPriorityThan` and `haTer:lowerPriority` to `ha:hasHigherPriorityThan`. Keep the subject and object in place. The legacy definitions describe the object's priority, and the target names describe the subject's priority (M03). |
| `motivation.skos.ttl`, `rights-statement.skos.ttl` | Replace `haRig:Motivation` and `dct:RightsStatement` types with `ha:Motivation` and `ha:RightsStatement`, respectively (M17). |
| `organization-logos.skos.ttl` | Replace the superclass `haOrg:Logo` with `ha:Logo` on `rdfs:subClassOf` statements. |
| `organization-types.skos.ttl` | Add `ha:OrganizationType` alongside `skos:Concept`. |
| `permission.skos.ttl` | Apply the rights operand and action mappings above. Also map the legacy `haRig:education` recipient to `ha:educational-public`. Preserve permission IRIs and the ODRL constraint structure. |
| `production-method.skos.ttl` | Add `ha:ProductionMethod` alongside `skos:Concept` (M11). |
| `reuse-licenses.skos.ttl` | Replace `schema:position` with `ha:hasPosition`, preserving the integer ordering. Review the target domain before reasoning over these ranks, since it covers intellectual entities, collections and cast entries. |
| `rotational-speed.skos.ttl` | Replace `http://schema.org/QualitativeValue` with `ha:QuantitativeValue` on numeric concepts. Replace `http://schema.org/value`, `http://schema.org/unitCode` and `http://schema.org/unitText` with `ha:hasMeasurementValue`, `ha:hasUnitCode` and `ha:hasUnitText`, respectively. Add the `ha:QuantitativeValue` type and RPM units to `variable` as specified in M05. |

## Execution plan

### 1. Record the model decisions before enabling affected rules

Assign the open post, format-classification, publication-issue typing, issuance range and identifier-domain decisions to the model owner. Rights-value decisions also need the rights-model owner, and URI-template and URL decisions need application-owner input. Use actual data examples to resolve the remaining REVIEW and UNMAPPED contexts. Record the accepted destination, condition, conversion, retained provenance and validation expectation for each open context.

The M02 agent fallback, descriptive role names, series positions, season numbers, transcripts, coverage and both hardware and software model strings can proceed under their stated rules. Profile fixity attribution (M13), ambiguous fragment offsets and media-file typing exceptions (M04), and timestamp conversions (M06). Align the affected draft shapes for role and agent links, decimal offsets, variable speed and EDTF dates before acceptance.

### 2. Profile the source dataset and preserve a reproducible baseline

Freeze the source ontology/vocabulary versions and take a restorable copy or immutable source graph. Count explicit class assertions, predicates and controlled-value IRIs from this inventory. Also list observed terms outside it, because SHACL describes supported usage rather than proving which triples actually exist. Profile literal datatypes/languages, node kinds, role-wrapper patterns, identifier-system boundaries, dates, offset precision, measurement units, and cross-links to vocabulary resources.

Record pre-existing source violations separately from problems introduced by migration. Specifically check checksum creator literals, agents represented by generic things, variable recording speed, series-level predecessors, and public-domain values.

### 3. Apply deterministic class and predicate rules into a new graph

Use an explicit IRI map, with subject-type/context guards where specified. Preserve resource identities, blank-node structure where possible, inverse directions and relation subtypes. Apply KEEP rules as well as MAP rules so externally named data is not dropped. Apply controlled-value rewrites throughout relevant data and load the target SKOS graphs with their existing concept and scheme IRIs.

Apply the fragment class mappings and media-file typing in M04 explicitly so they are available to SHACL Core. Use the approved conversion rules for datatypes and context-specific measurement values. Deduplicate identical output triples while recording many-to-one merges. Leave source graphs unchanged and keep unresolved statements in an identifiable legacy/provenance graph.

### 4. Run the approved structural and literal conversions

Handle roles, measurements, media offsets, dates, place and country resolution, country-name language tags, and caption models using the applicable M-rules. Reuse the existing local identifier nodes. Use deterministic identifiers for new nodes so reruns preserve their identities. Record original lexical values, language tags, predicates and conversion reasons where representation changes.

A rule that cannot establish its preconditions must produce an exception record containing the source subject, predicate, object, source graph, issue ID and reason. It must not discard the statement, fabricate precision, or silently substitute a generic value.

### 5. Validate coverage, semantics and application behavior

Write migration-specific acceptance checks from the agreed mapping decisions and source requirements. Align the draft target SHACL checks before using them for acceptance. Check the local identifier paths (M01), both forms of role names and the `ha:Agent` fallback (M02), decimal offsets (M04), variable recording speed (M05), date datatypes (M06), country-name datatype (M07), publication-issue typing (M10), production-method and issuance classes (M11), creation-place path (M12), metadata scope class (M17), and the allowed event outcome IRIs.

| Check | Acceptance criterion |
| --- | --- |
| Inventory coverage | Every observed source class/property/value is mapped, explicitly kept, or reported as unresolved; no unclassified drops. |
| Target existence | Every emitted target class/property is declared in the model, one of its supplied imports, or an explicitly approved foundational/extension vocabulary. Flag undefined references such as `ha:description` in the PREMIS extract and `ha:MetadataRScope` in the draft shape. |
| Controlled vocabularies | Load the target SKOS graphs and verify concept and scheme IRIs, labels and memberships. Check vocabulary types, format-priority directions, license ranks, numeric speed values and units, and the three event outcome types and IRIs. |
| Value preservation | All multilingual texts, date precision, identifier lexical forms, checksum values, measurement units and status notes survive or have an explicit loss/exception decision. |
| Context rules | Validate work and role chains, fixity attribution, and model strings on both agent types. Confirm that agents of unknown specific type are explicitly typed `ha:Agent` and keep their original links. Verify that generic generated resources and Mediahaven provenance retain their original scope. |
| Relations | Structural versus generic membership and inclusion remain distinct; inverse-copy edges remain consistent; sequence edges retain their direction. Newspaper predecessor links stay at series level. |
| Media | Source-file links connect `ha:MediaFile` and `ha:MediaFragment` in the original direction. Media files have a qualifying MIME type. Fragments preserve intellectual-entity and annotation links, and converted offsets use `xsd:decimal` seconds with source precision. |
| Rights | Policy targets, actions, permissions/prohibitions, constraints and motivations retain their behavior; operand IRIs/types and public-domain status patterns are correct. |
| Counts | Reconcile changes using per-rule counts. Track newly created measurement nodes, any materialized PREMIS identifier links, and merged annotation-subject triples. |
| Repeatability | Rerunning against the same frozen input produces the same graph, no duplicate generated nodes and the same exception ledger. |
| Application checks | Compare representative searches, resource displays, collection navigation, media clips, captions, request forms and rights evaluations before and after migration. |

Run checks on a sample spanning all used shapes, then the full dataset. Test both the chosen explicit-data model and any reasoning profile the applications actually use; domain/range inferences must not accidentally turn collections into intellectual works or identifier values into measurements.

### 6. Cut over only after reconciliation

Keep a mapping-version identifier, baseline counts, conversion/exception totals and validation results with the migrated graph. Update affected producers, queries, indexes and applications against the concrete crosswalk, then perform a staged read comparison. Resolve or explicitly accept remaining exceptions before retiring legacy reads. Keep the old graph available for rollback until operational checks pass; removal of old data is a separate deployment decision.

## Deliverable verification and limits

All five source shape files, the target RDFS model and its three supplied external extracts were parsed as Turtle. The crosswalk contains one entry for each of the **90 classes and 211 properties** found through active shape statements. The controlled-value crosswalk and M03 account for all **64 distinct values** from active source `sh:in` lists. Direct MAP/CHANGE/KEEP destinations were checked for declaration in the inspected target definitions, with the explicitly retained foundational RDF/SKOS terms allowed.

The 26 November revision checks the revised mappings against the current target RDFS and draft SHACL. The rotational-speed vocabulary has a Turtle syntax error at `variable` (M05). The marked REVIEW and UNMAPPED cases identify exceptions to automatic migration. Production profiling and validation belong to the execution phase.
