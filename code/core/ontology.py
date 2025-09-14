"""
Ontology Service

This module provides high-level ontology operations using Neo4j as the backend.
It supports creating nodes, properties, relationships, and provides ontology-specific
query capabilities for building knowledge graphs and semantic systems.
"""

from typing import Dict, List, Optional, Any, Union, Tuple
from utils.databases.neo4j import Neo4jService
from utils.databases import create_neo4j_service
from public.public_variable import logger
import traceback
from datetime import datetime

class OntologyService:
    """
    High-level ontology service for building knowledge graphs using Neo4j.
    
    This service provides ontology-specific operations including:
    - Creating ontology nodes (Classes, Concepts, Instances)
    - Managing properties and relationships
    - Ontology reasoning and validation
    - Summary and analytics methods
    """
    
    def __init__(self, 
                 neo4j_service: Optional[Neo4jService] = None,
                 labels_to_constrain: List[str] = ["Concept", "Instance", "Property", "Class", "Individual"]):
        """
        Initialize the ontology service
        
        Args:
            neo4j_service: Optional Neo4j service instance. If not provided,
                          will create one using configuration
        """
        self.neo4j = neo4j_service or create_neo4j_service()
        self.labels_to_constrain = labels_to_constrain
        if not self.neo4j:
            raise ValueError("Neo4j service could not be created. Check your configuration.")
        
        logger.info("OntologyService initialized successfully")
    
    # =============================================================================
    # Uniqueness Constraint Management
    # =============================================================================
    
    async def setup_uniqueness_constraints(self) -> Dict[str, Any]:
        """
        Set up uniqueness constraints on the 'name' property for all node types.
        This ensures no duplicate names within each node type.
        
        Returns:
            Dictionary containing information about created constraints
        """
        try:
            constraints_created = []
            
            for label in self.labels_to_constrain:
                try:
                    constraint_query = f"CREATE CONSTRAINT unique_{label.lower()}_name IF NOT EXISTS FOR (n:{label}) REQUIRE n.name IS UNIQUE"
                    await self.neo4j.execute_write(constraint_query)
                    constraints_created.append(label)
                    logger.info(f"Created unique constraint for {label}.name")
                except Exception as e:
                    logger.warning(f"Failed to create constraint for {label}: {str(e)}")
            
            result = {
                "constraints_created": constraints_created,
                "total_created": len(constraints_created)
            }
            
            logger.info(f"Setup completed: {len(constraints_created)} uniqueness constraints created")
            return result
            
        except Exception as e:
            logger.error(f"Failed to setup uniqueness constraints: {str(e)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to setup uniqueness constraints: {str(e)}")
    
    async def drop_uniqueness_constraints(self) -> Dict[str, Any]:
        """
        Drop all uniqueness constraints on the 'name' property.
        Use with caution - this will allow duplicate names.
        
        Returns:
            Dictionary containing information about dropped constraints
        """
        try:
            constraints_dropped = []
            
            for label in self.labels_to_constrain:
                try:
                    constraint_query = f"DROP CONSTRAINT unique_{label.lower()}_name IF EXISTS"
                    await self.neo4j.execute_write(constraint_query)
                    constraints_dropped.append(label)
                    logger.info(f"Dropped unique constraint for {label}.name")
                except Exception as e:
                    logger.warning(f"Failed to drop constraint for {label}: {str(e)}")
            
            result = {
                "constraints_dropped": constraints_dropped,
                "total_dropped": len(constraints_dropped)
            }
            
            logger.info(f"Cleanup completed: {len(constraints_dropped)} uniqueness constraints dropped")
            return result
            
        except Exception as e:
            logger.error(f"Failed to drop uniqueness constraints: {str(e)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to drop uniqueness constraints: {str(e)}")
    
    async def check_name_exists(self, name: str, label: Optional[str] = None) -> bool:
        """
        Check if a node with the given name already exists
        
        Args:
            name: Name to check for
            label: Optional label to limit the search to specific node type
            
        Returns:
            True if name exists, False otherwise
        """
        try:
            if label:
                query = f"MATCH (n:{label} {{name: $name}}) RETURN count(n) > 0 as exists"
            else:
                query = "MATCH (n {name: $name}) RETURN count(n) > 0 as exists"
            
            result = await self.neo4j.run_query_value(query, {"name": name}, key="exists")
            return bool(result)
            
        except Exception as e:
            logger.error(f"Failed to check if name exists: {str(e)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to check if name exists: {str(e)}")
    
    async def get_existing_node(self, name: str, label: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get an existing node with the given name
        
        Args:
            name: Name of the node to find
            label: Optional label to limit the search to specific node type
            
        Returns:
            Node data if found, None otherwise
        """
        try:
            if label:
                query = f"MATCH (n:{label} {{name: $name}}) RETURN n"
            else:
                query = "MATCH (n {name: $name}) RETURN n"
            
            result = await self.neo4j.run_query_single(query, {"name": name})
            return result.get("n") if result else None
            
        except Exception as e:
            logger.error(f"Failed to get existing node: {str(e)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to get existing node: {str(e)}")
    
    async def get_required_properties_for_concept(
        self, 
        concept_name: str, 
        concept_label: str = "Class",
        include_inherited: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get all required properties for a specific concept/class (supports multi-level inheritance)
        
        Args:
            concept_name: Name of the concept/class
            concept_label: Label of the concept node (Class, Concept, etc.)
            include_inherited: Whether to include required properties inherited from parent concepts
            
        Returns:
            List of required property information including inheritance details
        """
        try:
            required_properties = []
            
            # Get direct required properties
            direct_query = f"""
            MATCH (c:{concept_label} {{name: $concept_name}})-[r:HAS_PROPERTY]->(p:Property)
            WHERE r.required = true
            RETURN p.name as property_name, 
                   p.property_type as property_type,
                   p.range as range_type,
                   p.comment as comment,
                   p.tag as tag,
                   r.required as required,
                   COALESCE(r.default_value, null) as default_value,
                   'direct' as inheritance_type,
                   $concept_name as source_concept
            ORDER BY p.name
            """
            
            direct_props = await self.neo4j.run_query(direct_query, {"concept_name": concept_name})
            required_properties.extend(direct_props)
            
            if include_inherited:
                # Get inherited required properties from all parent concepts
                inherited_query = f"""
                MATCH (c:{concept_label} {{name: $concept_name}})-[:SUBCLASS_OF*]->(parent)-[r:HAS_PROPERTY]->(p:Property)
                WHERE r.required = true
                AND NOT EXISTS {{
                    MATCH (c)-[:SUBCLASS_OF*0..]->(intermediate)-[:HAS_PROPERTY]->(p)
                    WHERE intermediate.name <> parent.name 
                    AND (c)-[:SUBCLASS_OF*]->(intermediate)-[:SUBCLASS_OF*]->(parent)
                }}
                RETURN DISTINCT p.name as property_name, 
                       p.property_type as property_type,
                       p.range as range_type,
                       p.comment as comment,
                       p.tag as tag,
                       r.required as required,
                       COALESCE(r.default_value, null) as default_value,
                       'inherited' as inheritance_type,
                       parent.name as source_concept
                ORDER BY parent.name, p.name
                """
                
                inherited_props = await self.neo4j.run_query(inherited_query, {"concept_name": concept_name})
                
                # Filter out properties that are overridden by direct properties
                direct_prop_names = {prop["property_name"] for prop in direct_props}
                for inherited_prop in inherited_props:
                    if inherited_prop["property_name"] not in direct_prop_names:
                        required_properties.append(inherited_prop)
            
            logger.debug(f"Found {len(required_properties)} required properties for {concept_label} '{concept_name}' (including inherited: {include_inherited})")
            return required_properties
            
        except Exception as e:
            logger.error(f"Failed to get required properties for concept '{concept_name}': {str(e)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to get required properties: {str(e)}")
    
    async def validate_instance_properties(
        self,
        concept_name: str,
        provided_properties: Dict[str, Any],
        concept_label: str = "Class",
        include_inherited: bool = True
    ) -> Dict[str, Any]:
        """
        Validate that all required properties are provided for an instance (supports inheritance)
        
        Args:
            concept_name: Name of the concept/class
            provided_properties: Properties provided for the instance
            concept_label: Label of the concept node
            include_inherited: Whether to validate inherited required properties
            
        Returns:
            Dictionary containing validation results with inheritance details
            
        Raises:
            Exception: If validation fails
        """
        try:
            required_props = await self.get_required_properties_for_concept(
                concept_name, concept_label, include_inherited
            )
            
            missing_props = []
            missing_direct = []
            missing_inherited = []
            provided_prop_names = set(provided_properties.keys()) if provided_properties else set()
            
            for req_prop in required_props:
                prop_name = req_prop["property_name"]
                if prop_name not in provided_prop_names:
                    prop_info = {
                        "name": prop_name,
                        "type": req_prop.get("property_type", "Unknown"),
                        "range": req_prop.get("range_type", "Unknown"), 
                        "comment": req_prop.get("comment", ""),
                        "tag": req_prop.get("tag", ""),
                        "inheritance_type": req_prop.get("inheritance_type", "unknown"),
                        "source_concept": req_prop.get("source_concept", "unknown"),
                        "default_value": req_prop.get("default_value")
                    }
                    missing_props.append(prop_info)
                    
                    # Categorize by inheritance type
                    if req_prop.get("inheritance_type") == "direct":
                        missing_direct.append(prop_info)
                    elif req_prop.get("inheritance_type") == "inherited":
                        missing_inherited.append(prop_info)
            
            # Count properties by inheritance type
            direct_count = sum(1 for p in required_props if p.get("inheritance_type") == "direct")
            inherited_count = sum(1 for p in required_props if p.get("inheritance_type") == "inherited")
            
            validation_result = {
                "valid": len(missing_props) == 0,
                "total_required": len(required_props),
                "direct_required": direct_count,
                "inherited_required": inherited_count,
                "provided_count": len(provided_prop_names),
                "missing_properties": missing_props,
                "missing_direct": missing_direct,
                "missing_inherited": missing_inherited,
                "required_properties": required_props,
                "inheritance_enabled": include_inherited
            }
            
            if not validation_result["valid"]:
                error_msg = f"❌ Missing required properties for {concept_label} '{concept_name}':\n"
                
                if missing_direct:
                    error_msg += f"\n🔴 Missing Direct Properties ({len(missing_direct)}):\n"
                    for prop in missing_direct:
                        default_info = f" [default: {prop['default_value']}]" if prop['default_value'] is not None else ""
                        error_msg += f"  • {prop['name']} ({prop['type']}){default_info} - {prop['comment']}\n"
                
                if missing_inherited:
                    error_msg += f"\n🟠 Missing Inherited Properties ({len(missing_inherited)}):\n"
                    for prop in missing_inherited:
                        default_info = f" [default: {prop['default_value']}]" if prop['default_value'] is not None else ""
                        error_msg += f"  • {prop['name']} ({prop['type']}){default_info} - from '{prop['source_concept']}' - {prop['comment']}\n"
                
                error_msg += f"\n📊 Summary:"
                error_msg += f"\n  • Required: {len(required_props)} total ({direct_count} direct + {inherited_count} inherited)"
                error_msg += f"\n  • Provided: {len(provided_prop_names)} properties"
                error_msg += f"\n  • Missing: {len(missing_props)} properties"
                
                logger.error(error_msg)
                raise Exception(error_msg)
            
            logger.info(f"✅ All required properties provided for {concept_label} '{concept_name}' ({direct_count} direct + {inherited_count} inherited)")
            return validation_result
            
        except Exception as e:
            if "Missing required properties" in str(e):
                raise  # Re-raise our validation error as-is
            logger.error(f"Failed to validate instance properties: {str(e)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to validate instance properties: {str(e)}")
    
    async def find_nodes_by_name(self, name: str) -> List[Dict[str, Any]]:
        """
        Find all nodes with a given name across all labels
        
        Args:
            name: Name to search for
            
        Returns:
            List of dictionaries containing node information and labels
        """
        try:
            query = """
            MATCH (n {name: $name})
            RETURN n.name as name, labels(n) as labels, properties(n) as properties
            ORDER BY labels(n)
            """
            
            result = await self.neo4j.run_query(query, {"name": name})
            
            logger.debug(f"Found {len(result)} nodes with name '{name}'")
            return result
            
        except Exception as e:
            logger.error(f"Failed to find nodes by name '{name}': {str(e)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to find nodes by name: {str(e)}")
    
    async def _identify_property_types(self, property_names: List[str]) -> Dict[str, str]:
        """
        Identify the property types (DataProperty vs ObjectProperty) for given property names
        
        Args:
            property_names: List of property names to check
            
        Returns:
            Dictionary mapping property name to property type
        """
        try:
            if not property_names:
                return {}
            
            # Query to get property types for multiple properties
            query = """
            MATCH (p:Property)
            WHERE p.name IN $property_names
            RETURN p.name as property_name, p.property_type as property_type
            """
            
            result = await self.neo4j.run_query(query, {"property_names": property_names})
            
            property_types = {}
            for row in result:
                prop_name = row.get("property_name")
                prop_type = row.get("property_type", "DataProperty")  # Default to DataProperty
                if prop_name:
                    property_types[prop_name] = prop_type
            
            # For properties not found in the graph, default to DataProperty
            for prop_name in property_names:
                if prop_name not in property_types:
                    property_types[prop_name] = "DataProperty"
                    logger.warning(f"Property '{prop_name}' not found in graph, defaulting to DataProperty")
            
            logger.debug(f"Identified property types: {property_types}")
            return property_types
            
        except Exception as e:
            logger.error(f"Failed to identify property types: {str(e)}")
            # Default all to DataProperty if identification fails
            return {name: "DataProperty" for name in property_names}

    async def auto_detect_domain_label(self, domain_name: str) -> str:
        """
        Automatically detect the label of a domain node by name
        
        Args:
            domain_name: Name of the domain to find
            
        Returns:
            The detected label of the domain node
            
        Raises:
            Exception: If domain doesn't exist or if multiple nodes with same name exist
        """
        try:
            nodes = await self.find_nodes_by_name(domain_name)
            
            if not nodes:
                raise Exception(f"❌ Domain '{domain_name}' does not exist in the graph")
            
            if len(nodes) == 1:
                node_labels = nodes[0]["labels"]
                # Find the primary label (prefer Class, Concept, Instance, etc.)
                # priority_labels = ["Class", "Concept", "Instance", "Property", "Individual"]
                priority_labels = self.labels_to_constrain
                
                primary_label = None
                for priority_label in priority_labels:
                    if priority_label in node_labels:
                        primary_label = priority_label
                        break
                
                if not primary_label:
                    # Use the first label if no priority label found
                    primary_label = node_labels[0] if node_labels else "Node"
                
                logger.info(f"🔍 Auto-detected domain label: '{domain_name}' -> {primary_label}")
                return primary_label
            
            else:
                # Multiple nodes with same name - this is a conflict
                label_info = []
                for node in nodes:
                    labels_str = ", ".join(node["labels"])
                    label_info.append(f"  • {labels_str}")
                
                error_msg = f"❌ Multiple nodes found with name '{domain_name}':\n" + "\n".join(label_info)
                error_msg += f"\n\n💡 Please specify 'domain_label' parameter to disambiguate."
                raise Exception(error_msg)
                
        except Exception as e:
            if "Multiple nodes found" in str(e) or "does not exist" in str(e):
                raise  # Re-raise our specific errors
            logger.error(f"Failed to auto-detect domain label for '{domain_name}': {str(e)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to auto-detect domain label: {str(e)}")
    
    async def ping(self) -> bool:
        """Test connectivity to the Neo4j database"""
        return await self.neo4j.ping()
    
    async def close(self):
        """Close the Neo4j connection"""
        if self.neo4j:
            await self.neo4j.close()
            logger.info("OntologyService closed")
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    # =============================================================================
    # Common Properties Management
    # =============================================================================
    
    def _add_common_properties(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add common properties that all nodes should have: name, comment, tag
        
        Args:
            properties: Existing properties dictionary
            
        Returns:
            Properties dictionary with common properties added
        """
        # Ensure common properties exist
        if "comment" not in properties:
            properties["comment"] = ""
        if "tag" not in properties:
            properties["tag"] = ""
        
        # Add timestam
        properties["created_at"] = datetime.now().isoformat()
        
        return properties
    
    async def _create_node_with_merge(
        self,
        label: str,
        name: str,
        properties: Dict[str, Any],
        additional_labels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a node using MERGE to ensure uniqueness
        
        Args:
            label: Primary label for the node
            name: Name of the node (used as unique identifier)
            properties: All properties for the node
            additional_labels: Additional labels for the node
            
        Returns:
            Dictionary containing creation statistics and node info
        """
        try:
            # Build labels string
            labels_list = [label]
            if additional_labels:
                labels_list.extend(additional_labels)
            labels_str = ":".join(labels_list)
            
            # Build properties string for Cypher
            props_items = []
            for key, value in properties.items():
                if isinstance(value, str):
                    props_items.append(f"{key}: '{value}'")
                else:
                    props_items.append(f"{key}: {value}")
            props_str = ", ".join(props_items)
            
            # Use MERGE to create or match existing node
            query = f"""
            MERGE (n:{labels_str} {{name: $name}})
            ON CREATE SET n += $properties
            RETURN n
            """
            
            result = await self.neo4j.execute_write(query, {
                "name": name,
                "properties": properties
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to create node with MERGE: {str(e)}")
            raise
    
    async def _update_node(
        self,
        name: str,
        label: str,
        properties: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing node with new properties
        
        Args:
            name: Name of the node to update
            label: Label of the node
            properties: Properties to update
            
        Returns:
            Dictionary containing update statistics and node info
        """
        try:
            # Add updated timestamp
            properties["updated_at"] = datetime.now().isoformat()
            
            # Build SET clause for properties
            set_clauses = []
            for key, value in properties.items():
                set_clauses.append(f"n.{key} = ${key}")
            set_clause = ", ".join(set_clauses)
            
            query = f"""
            MATCH (n:{label} {{name: $name}})
            SET {set_clause}
            RETURN n
            """
            
            params = {"name": name}
            params.update(properties)
            
            result = await self.neo4j.execute_write(query, params)
            
            return {
                'records': result.get('records', []),
                'nodes_created': 0,
                'nodes_updated': 1,
                'properties_set': len(properties),
                'status': 'updated'
            }
            
        except Exception as e:
            logger.error(f"Failed to update node: {str(e)}")
            raise
    
    async def _rename_node(
        self,
        old_name: str,
        label: str,
        new_name: str
    ) -> Dict[str, Any]:
        """
        Rename a node's `name` property safely, preserving relationships.
        
        Args:
            old_name: Current name of the node
            label: Label of the node
            new_name: Desired new name
        
        Returns:
            Dictionary containing update statistics and node info
        """
        try:
            if old_name == new_name:
                return {
                    'records': [],
                    'nodes_created': 0,
                    'nodes_updated': 0,
                    'properties_set': 0,
                    'status': 'no_op'
                }
            # Ensure source exists
            existing = await self.get_existing_node(old_name, label)
            if not existing:
                raise Exception(f"Node '{old_name}' with label '{label}' not found for rename")
            # Ensure no conflict on target name within the same label
            conflict = await self.check_name_exists(new_name, label)
            if conflict:
                raise Exception(f"Target name '{new_name}' already exists for label '{label}'")
            # Perform rename
            query = f"""
            MATCH (n:{label} {{name: $old_name}})
            SET n.name = $new_name, n.updated_at = $updated_at
            RETURN n
            """
            result = await self.neo4j.execute_write(query, {
                "old_name": old_name,
                "new_name": new_name,
                "updated_at": datetime.now().isoformat()
            })
            return {
                'records': result.get('records', []),
                'nodes_created': 0,
                'nodes_updated': 1,
                'properties_set': 1,
                'status': 'renamed'
            }
        except Exception as e:
            logger.error(f"Failed to rename node '{old_name}' -> '{new_name}' ({label}): {str(e)}")
            raise
    
    # =============================================================================
    # Node Creation Methods (Enhanced with Common Properties)
    # =============================================================================
    
    async def create_concept_node(
        self,
        concept_name: str,
        properties: Optional[Dict[str, Any]] = None,
        additional_labels: Optional[List[str]] = None,
        allow_update: bool = False
    ) -> Dict[str, Any]:
        """
        Create a concept node in the ontology with uniqueness protection
        
        Args:
            concept_name: Name of the concept
            properties: Dictionary of properties to attach to the node
            additional_labels: Additional labels beyond 'Concept'
            allow_update: If True, update existing node properties. If False, return existing node as-is
            
        Returns:
            Dictionary containing creation/update statistics and node info
        """
        try:
            # Check if node already exists
            existing_node = await self.get_existing_node(concept_name, "Concept")
            
            if existing_node:
                if allow_update and properties:
                    # Update the existing node with new properties
                    logger.info(f"Updating existing concept node: {concept_name}")
                    return await self._update_node(concept_name, "Concept", properties)
                else:
                    # Return existing node without changes
                    logger.info(f"Concept node '{concept_name}' already exists, returning existing node")
                    return {
                        'records': [{'n': existing_node}],
                        'nodes_created': 0,
                        'nodes_updated': 0,
                        'properties_set': 0,
                        'status': 'already_exists'
                    }
            
            # Prepare properties with common properties
            node_properties = {"name": concept_name}
            if properties:
                node_properties.update(properties)
            
            # Add common properties (name, comment, tag, created_at)
            node_properties = self._add_common_properties(node_properties)
            
            # Use MERGE to ensure uniqueness at database level
            result = await self._create_node_with_merge(
                label="Concept",
                name=concept_name,
                properties=node_properties,
                additional_labels=additional_labels
            )
            
            logger.info(f"Created concept node: {concept_name}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to create concept node '{concept_name}': {str(e)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to create concept node: {str(e)}")
    
    async def create_instance_node(
        self,
        instance_name: str,
        concept_type: str,
        properties: Optional[Dict[str, Any]] = None,
        additional_labels: Optional[List[str]] = None,
        allow_update: bool = False,
        validate_required_properties: bool = True,
        concept_label: Optional[str] = None,  # Default to Class since you mentioned Class nodes
        auto_create_relationship: bool = True,
        auto_create_object_property_relationships: bool = True
    ) -> Dict[str, Any]:
        """
        Create an instance node that belongs to a concept with automatic IS_INSTANCE_OF relationship creation
        and automatic ObjectProperty relationship creation
        
        Args:
            instance_name: Name of the instance
            concept_type: The concept/class this instance belongs to
            properties: Dictionary of properties to attach to the node. ObjectProperty values can be either
                        single instance names (str) or lists of instance names (List[str]) to create
                        multiple relationships
            additional_labels: Additional labels beyond 'Instance'
            allow_update: If True, update existing node properties. If False, return existing node as-is
            validate_required_properties: If True, validate that all required properties are provided
            concept_label: Label of the concept node (Class, Concept, etc.)
            auto_create_relationship: If True, automatically create IS_INSTANCE_OF relationship with concept
            auto_create_object_property_relationships: If True, automatically create relationships for ObjectProperties
            
        Returns:
            Dictionary containing creation/update statistics and relationship info
            
        Raises:
            Exception: If required properties are missing, concept doesn't exist, or validation fails
        """
        try:
            # Handle a potential requested rename (properties.name)
            requested_new_name = None
            if properties and isinstance(properties.get("name", None), str):
                requested_new_name = properties.get("name")
            
            # Validate that concept exists if auto-relationship is enabled
            if auto_create_relationship:
                if not concept_label:
                    concept_label = await self.auto_detect_domain_label(concept_type)
                concept_node = await self.get_existing_node(concept_type, concept_label)
                if not concept_node:
                    error_msg = f"❌ Concept '{concept_type}' with label '{concept_label}' does not exist in the graph. Cannot create instance '{instance_name}' for non-existent concept."
                    logger.error(error_msg)
                    raise Exception(error_msg)
                logger.info(f"✅ Concept '{concept_type}' ({concept_label}) exists, proceeding with instance creation")
            
            # Separate properties into DataProperties and ObjectProperties
            data_properties = {}
            object_properties = {}
            
            if properties:
                # Exclude common property 'name' from typed property handling
                property_names = [p for p in properties.keys() if p != "name"]
                property_types = await self._identify_property_types(property_names)
                
                for prop_name, prop_value in properties.items():
                    if prop_name == "name":
                        continue
                    prop_type = property_types.get(prop_name, "DataProperty")
                    if prop_type == "ObjectProperty":
                        object_properties[prop_name] = prop_value
                        logger.debug(f"Identified ObjectProperty: {prop_name} -> {prop_value}")
                    else:
                        data_properties[prop_name] = prop_value
                        logger.debug(f"Identified DataProperty: {prop_name} = {prop_value}")
                
                logger.info(f"Separated properties: {len(data_properties)} DataProperties, {len(object_properties)} ObjectProperties")

            # Validate required properties if validation is enabled
            if validate_required_properties and properties:
                # Exclude common property 'name' from validation inputs
                validation_props = {k: v for k, v in properties.items() if k != "name"}
                await self.validate_instance_properties(concept_type, validation_props, concept_label)
            elif validate_required_properties:
                # Check if there are any required properties even when none provided
                await self.validate_instance_properties(concept_type, {}, concept_label)
            
            # Validate ObjectProperty targets exist if auto-creation is enabled
            if auto_create_object_property_relationships and object_properties:
                await self._validate_object_property_targets(object_properties)
            
            # Check if node already exists
            existing_node = await self.get_existing_node(instance_name, "Instance")
            
            if existing_node:
                if allow_update and properties:
                    # Re-validate if updating with new properties
                    if validate_required_properties:
                        # Get existing properties and merge with new ones for validation
                        existing_props = dict(existing_node)
                        existing_props.update({k: v for k, v in (properties or {}).items() if k != "name"})
                        await self.validate_instance_properties(concept_type, existing_props, concept_label)
                    
                    # If a rename is requested, perform it first and update local variable
                    if requested_new_name and requested_new_name != instance_name:
                        logger.info(f"Renaming Instance '{instance_name}' -> '{requested_new_name}'")
                        await self._rename_node(instance_name, "Instance", requested_new_name)
                        instance_name = requested_new_name
                    
                    # Update the existing node with new properties (only DataProperties)
                    logger.info(f"Updating existing instance node: {instance_name}")
                    update_result = await self._update_node(instance_name, "Instance", data_properties)
                    
                    # Handle ObjectProperty relationships for updated node
                    if auto_create_object_property_relationships and object_properties:
                        obj_rel_results = await self._replace_object_property_relationships(
                            instance_name, object_properties
                        )
                        update_result["object_property_relationships"] = obj_rel_results
                    
                    return update_result
                else:
                    # If rename requested but updates not allowed
                    if requested_new_name and requested_new_name != instance_name:
                        raise Exception("Rename requested but allow_update is False")
                    # Return existing node without changes
                    logger.info(f"Instance node '{instance_name}' already exists, returning existing node")
                    return {
                        'records': [{'n': existing_node}],
                        'nodes_created': 0,
                        'nodes_updated': 0,
                        'properties_set': 0,
                        'status': 'already_exists',
                        'auto_relationship_created': False
                    }
            
            # Prepare properties with common properties (only DataProperties)
            final_instance_name = requested_new_name or instance_name
            node_properties = {
                "name": final_instance_name,
                "instance_of": concept_type
            }
            if data_properties:
                node_properties.update(data_properties)
            
            # Add common properties (name, comment, tag, created_at)
            node_properties = self._add_common_properties(node_properties)
            
            # Use MERGE to ensure uniqueness at database level
            result = await self._create_node_with_merge(
                label="Instance",
                name=final_instance_name,
                properties=node_properties,
                additional_labels=additional_labels
            )
            
            logger.info(f"Created instance node: {final_instance_name} of type {concept_type}")
            
            # Automatically create IS_INSTANCE_OF relationship if enabled
            if auto_create_relationship:
                try:
                    logger.info(f"🔗 Auto-creating IS_INSTANCE_OF relationship: {final_instance_name} -> {concept_type}")
                    
                    # Create the IS_INSTANCE_OF relationship
    
                    rel_properties = {"created_at": datetime.now().isoformat()}
                    
                    relationship_result = await self.neo4j.create_relationship(
                        from_node_query=":Instance {name: $instance_name}",
                        to_node_query=f":{concept_label} {{name: $concept_name}}",
                        relationship_type="IS_INSTANCE_OF",
                        properties=rel_properties,
                        from_params={"instance_name": final_instance_name},
                        to_params={"concept_name": concept_type}
                    )
                    
                    logger.info(f"✅ Successfully created IS_INSTANCE_OF relationship: {final_instance_name} -> {concept_type}")
                    
                    # Combine the results
                    result["auto_relationship_created"] = True
                    result["relationships_created"] = relationship_result.get("relationships_created", 0)
                    
                except Exception as rel_error:
                    logger.warning(f"⚠️ Instance '{final_instance_name}' created but failed to create IS_INSTANCE_OF relationship: {str(rel_error)}")
                    result["auto_relationship_created"] = False
                    result["relationship_error"] = str(rel_error)
            else:
                result["auto_relationship_created"] = False
            
            # Create ObjectProperty relationships if enabled
            if auto_create_object_property_relationships and object_properties:
                try:
                    logger.info(f"🔗 Auto-creating ObjectProperty relationships for {len(object_properties)} properties")
                    
                    obj_rel_results = await self._create_object_property_relationships(
                        final_instance_name, object_properties
                    )
                    
                    result["object_property_relationships"] = obj_rel_results
                    result["object_properties_created"] = len([r for r in obj_rel_results if r.get("success", False)])
                    result["object_properties_failed"] = len([r for r in obj_rel_results if not r.get("success", False)])
                    
                    # Update total relationships created
                    total_obj_rels = sum(r.get("relationships_created", 0) for r in obj_rel_results if r.get("success", False))
                    result["relationships_created"] = result.get("relationships_created", 0) + total_obj_rels
                    
                    logger.info(f"✅ ObjectProperty relationships: {result['object_properties_created']} created, {result['object_properties_failed']} failed")
                    
                except Exception as obj_error:
                    logger.warning(f"⚠️ Instance '{instance_name}' created but failed to create ObjectProperty relationships: {str(obj_error)}")
                    result["object_property_error"] = str(obj_error)
                    result["object_properties_created"] = 0
                    result["object_properties_failed"] = len(object_properties)
            else:
                result["object_properties_created"] = 0
                result["object_properties_failed"] = 0
            
            # Calculate total operations
            operations = 1  # Instance creation
            if result.get("auto_relationship_created", False):
                operations += 1
            operations += result.get("object_properties_created", 0)
            result["total_operations"] = operations
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to create instance node '{instance_name}': {str(e)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to create instance node: {str(e)}")
    
    async def create_property_node(
        self,
        property_name: str,
        property_type: str = "DataProperty",
        domain: Optional[str] = None,
        range_type: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        auto_create_relationship: bool = True,
        domain_label: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a property node in the ontology with automatic domain relationship creation
        
        Args:
            property_name: Name of the property
            property_type: Type of property (DataProperty, ObjectProperty, etc.)
            domain: The concept/class that this property applies to
            range_type: The type/range of values this property can have
            properties: Additional properties
            auto_create_relationship: If True, automatically create HAS_PROPERTY relationship with domain
            domain_label: Label of the domain node (Class, Concept, etc.). If None, will auto-detect
            
        Returns:
            Dictionary containing creation statistics and node info
            
        Raises:
            Exception: If domain is specified but doesn't exist in the graph
        """
        try:
            # Auto-detect domain label if not provided
            if domain and not domain_label:
                domain_label = await self.auto_detect_domain_label(domain)
            
            # Validate domain exists if specified and auto-relationship is enabled
            if domain and auto_create_relationship:
                domain_node = await self.get_existing_node(domain, domain_label)
                if not domain_node:
                    error_msg = f"❌ Domain '{domain}' with label '{domain_label}' does not exist in the graph. Cannot create property '{property_name}' with non-existent domain."
                    logger.error(error_msg)
                    raise Exception(error_msg)
                logger.info(f"✅ Domain '{domain}' ({domain_label}) exists, proceeding with property creation")
            
            # Prepare properties with common properties
            node_properties = {
                "name": property_name,
                "property_type": property_type
            }
            
            if domain:
                node_properties["domain"] = domain
            if range_type:
                node_properties["range"] = range_type
            if properties:
                node_properties.update(properties)
            
            # Add common properties (name, comment, tag, created_at)
            node_properties = self._add_common_properties(node_properties)
            
            # Create the property node
            result = await self.neo4j.create_node(
                label="Property",
                properties=node_properties,
                additional_labels=[property_type] if property_type != "Property" else None
            )
            
            logger.info(f"Created property node: {property_name} ({property_type})")
            
            # Automatically create HAS_PROPERTY relationship if domain is specified
            if domain and auto_create_relationship:
                try:
                    logger.info(f"🔗 Auto-creating HAS_PROPERTY relationship: {domain} -> {property_name}")
                    
                    # Extract required flag from properties if provided
                    required = node_properties.get("required", False)
                    default_value = node_properties.get("default_value", None)
                    
                    relationship_result = await self.assign_property_to_concept(
                        concept_name=domain,
                        property_name=property_name,
                        required=required,
                        default_value=default_value,
                        concept_label=domain_label  # This will be the auto-detected or provided label
                    )
                    
                    logger.info(f"✅ Successfully created HAS_PROPERTY relationship: {domain} -> {property_name}")
                    
                    # Combine the results
                    result["auto_relationship_created"] = True
                    result["relationships_created"] = relationship_result.get("relationships_created", 0)
                    result["total_operations"] = 2  # Property creation + relationship creation
                    
                except Exception as rel_error:
                    logger.warning(f"⚠️ Property '{property_name}' created but failed to create HAS_PROPERTY relationship: {str(rel_error)}")
                    result["auto_relationship_created"] = False
                    result["relationship_error"] = str(rel_error)
            else:
                result["auto_relationship_created"] = False
                result["total_operations"] = 1  # Only property creation
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to create property node '{property_name}': {str(e)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to create property node: {str(e)}")
    
    async def create_custom_node(
        self,
        label: str,
        name: str,
        properties: Optional[Dict[str, Any]] = None,
        additional_labels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a custom node with specified label and properties
        
        Args:
            label: Primary label for the node
            name: Name of the node
            properties: Dictionary of properties to attach to the node
            additional_labels: Additional labels for the node
            
        Returns:
            Dictionary containing creation statistics and node info
        """
        try:
            # Prepare properties with common properties
            node_properties = {"name": name}
            if properties:
                node_properties.update(properties)
            
            # Add common properties (name, comment, tag, created_at)
            node_properties = self._add_common_properties(node_properties)
            
            # Create the node
            result = await self.neo4j.create_node(
                label=label,
                properties=node_properties,
                additional_labels=additional_labels
            )
            
            logger.info(f"Created custom node: {name} with label {label}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to create custom node '{name}': {str(e)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to create custom node: {str(e)}")
    
    # =============================================================================
    # ObjectProperty Helper Methods
    # =============================================================================
    
    async def _validate_object_property_targets(self, object_properties: Dict[str, Any]) -> None:
        """
        Validate that all ObjectProperty target instances exist in the graph
        
        Args:
            object_properties: Dictionary of ObjectProperty names and their target instance names
                              Values can be either single instance names (str) or lists of instance names (List[str])
            
        Raises:
            Exception: If any target instance doesn't exist
        """
        try:
            missing_targets = []
            total_targets = 0
            
            for prop_name, target_value in object_properties.items():
                # Handle both single instance and list of instances
                if isinstance(target_value, list):
                    target_names = target_value
                else:
                    target_names = [target_value]
                
                for target_name in target_names:
                    total_targets += 1
                    # Check if target instance exists
                    target_exists = await self.check_name_exists(target_name, "Instance")
                    
                    if not target_exists:
                        missing_targets.append({
                            "property": prop_name,
                            "target": target_name
                        })
                        logger.warning(f"ObjectProperty target not found: {prop_name} -> {target_name}")
                    else:
                        logger.debug(f"✅ ObjectProperty target exists: {prop_name} -> {target_name}")
            
            if missing_targets:
                error_msg = f"❌ ObjectProperty validation failed. Missing target instances:\n"
                for missing in missing_targets:
                    error_msg += f"  • Property '{missing['property']}' targets '{missing['target']}' (Instance not found)\n"
                error_msg += f"\n💡 Please create these Instance nodes before creating relationships to them."
                
                logger.error(error_msg)
                raise Exception(error_msg)
            
            logger.info(f"✅ All {total_targets} ObjectProperty targets validated successfully ({len(object_properties)} properties)")
            
        except Exception as e:
            if "ObjectProperty validation failed" in str(e):
                raise  # Re-raise validation errors as-is
            logger.error(f"Failed to validate ObjectProperty targets: {str(e)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to validate ObjectProperty targets: {str(e)}")
    
    async def _create_object_property_relationships(
        self,
        instance_name: str,
        object_properties: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Create relationships for ObjectProperties
        
        Args:
            instance_name: Name of the source instance
            object_properties: Dictionary of ObjectProperty names and their target instance names
                              Values can be either single instance names (str) or lists of instance names (List[str])
            
        Returns:
            List of relationship creation results
        """
        try:
            results = []
            
            for prop_name, target_value in object_properties.items():
                # Handle both single instance and list of instances
                if isinstance(target_value, list):
                    target_names = target_value
                else:
                    target_names = [target_value]
                
                # Create relationships for each target
                for target_name in target_names:
                    try:
                        logger.info(f"🔗 Creating ObjectProperty relationship: {instance_name} -[{prop_name}]-> {target_name}")
                        
                        # Create relationship with property metadata
        
                        rel_properties = {
                            "property_name": prop_name,
                            "property_type": "ObjectProperty",
                            "created_at": datetime.now().isoformat()
                        }
                        
                        # Sanitize relationship type (Neo4j relationship types have naming restrictions)
                        rel_type = prop_name.upper().replace(" ", "_").replace("-", "_")
                        
                        relationship_result = await self.neo4j.create_relationship(
                            from_node_query=":Instance {name: $from_instance}",
                            to_node_query=":Instance {name: $to_instance}",
                            relationship_type=rel_type,
                            properties=rel_properties,
                            from_params={"from_instance": instance_name},
                            to_params={"to_instance": target_name}
                        )
                        
                        # Check if relationship was skipped due to existing constraint
                        if self.neo4j.was_skipped_due_to_constraint(relationship_result):
                            logger.info(f"⚠️ ObjectProperty relationship already exists: {instance_name} -[{prop_name}]-> {target_name}")
                            results.append({
                                "property": prop_name,
                                "target": target_name,
                                "relationship_type": rel_type,
                                "success": True,
                                "status": "already_exists",
                                "relationships_created": 0,
                                "warning": self.neo4j.get_warning_message(relationship_result)
                            })
                        else:
                            logger.info(f"✅ Successfully created ObjectProperty relationship: {instance_name} -[{prop_name}]-> {target_name}")
                            results.append({
                                "property": prop_name,
                                "target": target_name,
                                "relationship_type": rel_type,
                                "success": True,
                                "status": "created",
                                "relationships_created": relationship_result.get("relationships_created", 1)
                            })
                        
                    except Exception as rel_error:
                        logger.error(f"❌ Failed to create ObjectProperty relationship {prop_name} -> {target_name}: {str(rel_error)}")
                        results.append({
                            "property": prop_name,
                            "target": target_name,
                            "relationship_type": prop_name.upper().replace(" ", "_").replace("-", "_"),
                            "success": False,
                            "error": str(rel_error),
                            "relationships_created": 0
                        })
            
            successful = len([r for r in results if r.get("success", False)])
            total_relationships = len(results)
            logger.info(f"ObjectProperty relationship creation completed: {successful}/{total_relationships} successful")
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to create ObjectProperty relationships: {str(e)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to create ObjectProperty relationships: {str(e)}")

    async def _replace_object_property_relationships(
        self,
        instance_name: str,
        object_properties: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Replace existing ObjectProperty relationships with the provided targets.
        For each property, delete all existing relationships of that type from the instance,
        then create new ones using _create_object_property_relationships.
        """
        try:
            results: List[Dict[str, Any]] = []
            # First, for each property, remove previous relationships of that property
            for prop_name, target_value in object_properties.items():
                rel_type = prop_name.upper().replace(" ", "_").replace("-", "_")
                await self.neo4j.run_query(
                    f"""
                    MATCH (:Instance {{name: $from_instance}})-[r:{rel_type}]->(:Instance)
                    DELETE r
                    """,
                    {"from_instance": instance_name}
                )
            # Then create new ones
            created = await self._create_object_property_relationships(instance_name, object_properties)
            results.extend(created)
            return results
        except Exception as e:
            logger.error(f"Failed to replace ObjectProperty relationships: {str(e)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to replace ObjectProperty relationships: {str(e)}")

    # =============================================================================
    # Relationship Creation Methods
    # =============================================================================
    
    async def create_subclass_relationship(
        self,
        subclass_name: str,
        superclass_name: str,
        properties: Optional[Dict[str, Any]] = None,
        subclass_label: str = "Concept",
        superclass_label: str = "Concept"
    ) -> Dict[str, Any]:
        """
        Create a subclass relationship between two nodes
        
        Args:
            subclass_name: Name of the subclass node
            superclass_name: Name of the superclass node
            properties: Additional properties for the relationship
            subclass_label: Label of the subclass node (default: "Concept")
            superclass_label: Label of the superclass node (default: "Concept")
            
        Returns:
            Dictionary containing relationship creation statistics
        """
        try:
            rel_properties = properties or {}
            
            # Add timestamp
            rel_properties["created_at"] = datetime.now().isoformat()
            
            result = await self.neo4j.create_relationship(
                from_node_query=f":{subclass_label} {{name: $subclass_name}}",
                to_node_query=f":{superclass_label} {{name: $superclass_name}}",
                relationship_type="SUBCLASS_OF",
                properties=rel_properties,
                from_params={"subclass_name": subclass_name},
                to_params={"superclass_name": superclass_name}
            )
            
            logger.info(f"Created SUBCLASS_OF relationship: {subclass_name} ({subclass_label}) -> {superclass_name} ({superclass_label})")
            return result
            
        except Exception as e:
            logger.error(f"Failed to create subclass relationship: {str(e)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to create subclass relationship: {str(e)}")
    
    async def create_instance_relationship(
        self,
        instance_name: str,
        concept_name: str,
        properties: Optional[Dict[str, Any]] = None,
        instance_label: str = "Instance",
        concept_label: str = "Concept"
    ) -> Dict[str, Any]:
        """
        Create an instance-of relationship between an instance and a concept
        
        Args:
            instance_name: Name of the instance
            concept_name: Name of the concept
            properties: Additional properties for the relationship
            
        Returns:
            Dictionary containing relationship creation statistics
        """
        try:
            rel_properties = properties or {}
            
            # Add timestamp
            rel_properties["created_at"] = datetime.now().isoformat()
            
            result = await self.neo4j.create_relationship(
                from_node_query=f":{instance_label} {{name: $instance_name}}",
                to_node_query=f":{concept_label} {{name: $concept_name}}",
                relationship_type="INSTANCE_OF",
                properties=rel_properties,
                from_params={"instance_name": instance_name},
                to_params={"concept_name": concept_name}
            )
            
            logger.info(f"Created INSTANCE_OF relationship: {instance_name} -> {concept_name}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to create instance relationship: {str(e)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to create instance relationship: {str(e)}")
    
    async def create_property_relationship(
        self,
        subject_name: str,
        property_name: str,
        object_name: str,
        subject_label: str = "Instance",
        object_label: str = "Instance",
        properties: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a property relationship between two nodes
        
        Args:
            subject_name: Name of the subject node
            property_name: Name of the property (becomes relationship type)
            object_name: Name of the object node
            subject_label: Label of the subject node
            object_label: Label of the object node
            properties: Additional properties for the relationship
            
        Returns:
            Dictionary containing relationship creation statistics
        """
        try:
            rel_properties = properties or {}
            rel_properties["property"] = property_name
            
            # Add timestamp
            rel_properties["created_at"] = datetime.now().isoformat()
            
            # Use property name as relationship type (sanitized)
            rel_type = property_name.upper().replace(" ", "_").replace("-", "_")
            
            result = await self.neo4j.create_relationship(
                from_node_query=f":{subject_label} {{name: $subject_name}}",
                to_node_query=f":{object_label} {{name: $object_name}}",
                relationship_type=rel_type,
                properties=rel_properties,
                from_params={"subject_name": subject_name},
                to_params={"object_name": object_name}
            )
            
            logger.info(f"Created {rel_type} relationship: {subject_name} -> {object_name}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to create property relationship: {str(e)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to create property relationship: {str(e)}")
    
    async def create_custom_relationship(
        self,
        from_node_name: str,
        to_node_name: str,
        relationship_type: str,
        from_label: str = "Concept",
        to_label: str = "Concept",
        properties: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a custom relationship between two nodes
        
        Args:
            from_node_name: Name of the source node
            to_node_name: Name of the target node
            relationship_type: Type of the relationship
            from_label: Label of the source node
            to_label: Label of the target node
            properties: Additional properties for the relationship
            
        Returns:
            Dictionary containing relationship creation statistics
        """
        try:
            rel_properties = properties or {}
            
            # Add timestamp
            rel_properties["created_at"] = datetime.now().isoformat()
            
            result = await self.neo4j.create_relationship(
                from_node_query=f":{from_label} {{name: $from_name}}",
                to_node_query=f":{to_label} {{name: $to_name}}",
                relationship_type=relationship_type,
                properties=rel_properties,
                from_params={"from_name": from_node_name},
                to_params={"to_name": to_node_name}
            )
            
            logger.info(f"Created {relationship_type} relationship: {from_node_name} -> {to_node_name}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to create custom relationship: {str(e)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to create custom relationship: {str(e)}")
    
    async def create_semantic_relationship(
        self,
        from_node_name: str,
        to_node_name: str,
        relationship_type: str,
        semantic_properties: Optional[Dict[str, Any]] = None,
        from_label: str = "Concept",
        to_label: str = "Concept"
    ) -> Dict[str, Any]:
        """
        Create a semantic relationship with ontology-specific properties
        
        Args:
            from_node_name: Name of the source node
            to_node_name: Name of the target node
            relationship_type: Type of semantic relationship (e.g., RELATED_TO, PART_OF, HAS_ATTRIBUTE)
            semantic_properties: Semantic properties like confidence, weight, etc.
            from_label: Label of the source node
            to_label: Label of the target node
            
        Returns:
            Dictionary containing relationship creation statistics
        """
        try:
            rel_properties = semantic_properties or {}
            
            # Add semantic metadata
            rel_properties.update({
                "semantic_type": relationship_type,
                "confidence": rel_properties.get("confidence", 1.0),
                "weight": rel_properties.get("weight", 1.0)
            })
            
            # Add timestamp
            rel_properties["created_at"] = datetime.now().isoformat()
            
            result = await self.neo4j.create_relationship(
                from_node_query=f":{from_label} {{name: $from_name}}",
                to_node_query=f":{to_label} {{name: $to_name}}",
                relationship_type=relationship_type,
                properties=rel_properties,
                from_params={"from_name": from_node_name},
                to_params={"to_name": to_node_name}
            )
            
            logger.info(f"Created semantic {relationship_type} relationship: {from_node_name} -> {to_node_name}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to create semantic relationship: {str(e)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to create semantic relationship: {str(e)}")
    
    # =============================================================================
    # Property Inheritance Methods
    # =============================================================================
    
    async def assign_property_to_concept(
        self,
        concept_name: str,
        property_name: str,
        required: bool = False,
        default_value: Optional[Any] = None,
        constraints: Optional[Dict[str, Any]] = None,
        concept_label: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Assign a property to a concept/class, creating a HAS_PROPERTY relationship
        
        Args:
            concept_name: Name of the concept/class
            property_name: Name of the property
            required: Whether this property is required for instances
            default_value: Default value for the property
            constraints: Additional constraints for the property
            concept_label: Label of the concept node (Concept, Class, etc.). If None, will auto-detect
            
        Returns:
            Dictionary containing relationship creation statistics
        """
        try:
            # Auto-detect concept label if not provided
            if not concept_label:
                concept_label = await self.auto_detect_domain_label(concept_name)
            
            rel_properties = {
                "required": required,
                "assignment_type": "direct"
            }
            
            if default_value is not None:
                rel_properties["default_value"] = default_value
            if constraints:
                rel_properties.update(constraints)
            
            # Add timestamp
            rel_properties["created_at"] = datetime.now().isoformat()
            
            result = await self.neo4j.create_relationship(
                from_node_query=f":{concept_label} {{name: $concept_name}}",
                to_node_query=":Property {name: $property_name}",
                relationship_type="HAS_PROPERTY",
                properties=rel_properties,
                from_params={"concept_name": concept_name},
                to_params={"property_name": property_name}
            )
            
            logger.info(f"Assigned property '{property_name}' to {concept_label.lower()} '{concept_name}'")
            return result
            
        except Exception as e:
            logger.error(f"Failed to assign property to concept: {str(e)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to assign property to concept: {str(e)}")
    
    async def get_concept_properties(
        self,
        concept_name: str,
        concept_label: Optional[str] = None,
        include_inherited: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get all properties associated with a concept, including inherited ones
        
        Args:
            concept_name: Name of the concept
            concept_label: Label of the concept
            include_inherited: Whether to include properties inherited from parent concepts
            
        Returns:
            List of properties with their constraints and inheritance info
        """
        try:
            properties = []
            if not concept_label:
                concept_label = await self.auto_detect_domain_label(concept_name)
            if concept_label == "Concept" or concept_label == "Class":
                pass
            else:
                raise Exception(f"This method only supports Concept or Class nodes, but got {concept_label}")
            # Get direct properties
            direct_query = f"""
            MATCH (c:{concept_label} {{name: $concept_name}})-[r:HAS_PROPERTY]->(p:Property)
            RETURN p.name as property_name, p as property_node, r as relationship,
                   'direct' as inheritance_type, c.name as source_concept
            """
            direct_props = await self.neo4j.run_query(direct_query, {"concept_name": concept_name})
            properties.extend(direct_props)
            
            if include_inherited:
                # Get inherited properties from all parent concepts
                inherited_query = f"""
                MATCH (c:{concept_label} {{name: $concept_name}})-[:SUBCLASS_OF*]->(parent:{concept_label})-[r:HAS_PROPERTY]->(p:Property)
                WHERE NOT (c)-[:HAS_PROPERTY]->(p)
                RETURN p.name as property_name, p as property_node, r as relationship,
                       'inherited' as inheritance_type, parent.name as source_concept
                ORDER BY parent.name
                """
                inherited_props = await self.neo4j.run_query(inherited_query, {"concept_name": concept_name})
                properties.extend(inherited_props)
            
            logger.debug(f"Retrieved {len(properties)} properties for concept '{concept_name}'")
            return properties
            
        except Exception as e:
            logger.error(f"Failed to get concept properties: {str(e)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to get concept properties: {str(e)}")
    
    async def check_property_inheritance(
        self,
        subclass_name: str,
        superclass_name: str,
        subclass_label: Optional[str] = None,
        superclass_label: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check what properties a subclass inherits from a superclass (supports multi-level inheritance)
        
        Args:
            subclass_name: Name of the subclass concept
            superclass_name: Name of the superclass concept
            subclass_label: Label of the subclass concept
            superclass_label: Label of the superclass concept
        Returns:
            Dictionary containing inheritance information including all inherited properties across multiple levels
        """
        try:
            # Auto-detect labels if not provided
            if not subclass_label:
                subclass_label = await self.auto_detect_domain_label(subclass_name)
            if not superclass_label:
                superclass_label = await self.auto_detect_domain_label(superclass_name)
            
            # Check if subclass relationship exists (fixed syntax)
            rel_check_query = f"""
            MATCH (sub:{subclass_label} {{name: $subclass_name}})-[:SUBCLASS_OF*]->(super:{superclass_label} {{name: $superclass_name}})
            RETURN count(*) as relationship_exists
            """
            rel_exists = await self.neo4j.run_query_value(
                rel_check_query, 
                {"subclass_name": subclass_name, "superclass_name": superclass_name},
                key="relationship_exists"
            )
            
            if not rel_exists:
                return {
                    "inheritance_exists": False,
                    "message": f"No subclass relationship between {subclass_name} and {superclass_name}"
                }
            
            # Get ALL properties available to superclass (direct + inherited from its ancestors)
            superclass_props_query = f"""
            MATCH (super:{superclass_label} {{name: $superclass_name}})
            MATCH (super)-[:SUBCLASS_OF*0..]->(ancestor)-[r:HAS_PROPERTY]->(p:Property)
            RETURN DISTINCT p.name as property_name, p as property_node, r as relationship,
                   ancestor.name as source_concept,
                   CASE WHEN ancestor.name = $superclass_name THEN 'direct' ELSE 'inherited' END as inheritance_type
            ORDER BY p.name
            """
            superclass_props = await self.neo4j.run_query(
                superclass_props_query, 
                {"superclass_name": superclass_name}
            )
            
            # Check which properties are overridden in subclass (considering subclass inheritance too)
            inherited_props = []
            overridden_props = []
            
            for prop in superclass_props:
                prop_name = prop["property_name"]
                
                # Check if subclass has its own version of this property (direct or inherited)
                override_check_query = f"""
                MATCH (sub:{subclass_label} {{name: $subclass_name}})
                MATCH (sub)-[:SUBCLASS_OF*0..]->(ancestor)-[:HAS_PROPERTY]->(p:Property {{name: $prop_name}})
                WHERE ancestor.name <> $superclass_name
                RETURN count(*) as has_override, collect(ancestor.name)[0] as override_source
                """
                override_result = await self.neo4j.run_query_single(
                    override_check_query,
                    {"subclass_name": subclass_name, "prop_name": prop_name, "superclass_name": superclass_name}
                )
                
                has_override = override_result.get("has_override", 0) if override_result else 0
                override_source = override_result.get("override_source") if override_result else None
                
                if has_override:
                    prop_info = dict(prop)
                    prop_info["override_source"] = override_source
                    overridden_props.append(prop_info)
                else:
                    inherited_props.append(prop)
            
            return {
                "inheritance_exists": True,
                "subclass": subclass_name,
                "superclass": superclass_name,
                "inherited_properties": inherited_props,
                "overridden_properties": overridden_props,
                "total_inherited": len(inherited_props),
                "total_overridden": len(overridden_props),
                "total_available_from_superclass": len(superclass_props)
            }
            
        except Exception as e:
            logger.error(f"Failed to check property inheritance: {str(e)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to check property inheritance: {str(e)}")
    
    # =============================================================================
    # Summary and Analytics Methods
    # =============================================================================
    
    async def get_node_count(self, label: Optional[str] = None) -> int:
        """
        Get the count of nodes in the ontology
        
        Args:
            label: Optional label to filter nodes. If None, returns total count
            
        Returns:
            Number of nodes matching the criteria
        """
        try:
            if label:
                query = f"MATCH (n:{label}) RETURN count(n) as count"
                result = await self.neo4j.run_query_value(query, key="count")
                logger.debug(f"Found {result} nodes with label '{label}'")
            else:
                query = "MATCH (n) RETURN count(n) as count"
                result = await self.neo4j.run_query_value(query, key="count")
                logger.debug(f"Found {result} total nodes")
            
            return result or 0
            
        except Exception as e:
            logger.error(f"Failed to get node count: {str(e)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to get node count: {str(e)}")
    
    async def get_ontology_summary(self) -> Dict[str, Any]:
        """
        Get a comprehensive summary of the ontology
        
        Returns:
            Dictionary containing various statistics about the ontology
        """
        try:
            summary = {}
            
            # Basic counts
            summary["total_nodes"] = await self.get_node_count()
            summary["total_relationships"] = await self.neo4j.run_query_value(
                "MATCH ()-[r]->() RETURN count(r) as count", key="count"
            ) or 0
            
            # Node counts by label
            summary["node_counts_by_label"] = {}
            labels_query = "CALL db.labels() YIELD label RETURN label"
            labels_result = await self.neo4j.run_query(labels_query)
            
            for row in labels_result:
                label = row.get("label")
                if label:
                    count = await self.get_node_count(label)
                    summary["node_counts_by_label"][label] = count
            
            # Relationship counts by type
            summary["relationship_counts_by_type"] = {}
            rel_types_query = """
            MATCH ()-[r]->()
            RETURN type(r) as relationship_type, count(r) as count
            ORDER BY count DESC
            """
            rel_types_result = await self.neo4j.run_query(rel_types_query)
            
            for row in rel_types_result:
                rel_type = row.get("relationship_type")
                count = row.get("count", 0)
                if rel_type:
                    summary["relationship_counts_by_type"][rel_type] = count
            
            # Ontology-specific metrics
            summary["concepts_count"] = await self.get_node_count("Concept")
            summary["instances_count"] = await self.get_node_count("Instance")
            summary["properties_count"] = await self.get_node_count("Property")
            
            # Hierarchy depth (for concepts)
            hierarchy_query = """
            MATCH path = (n:Concept)-[:SUBCLASS_OF*]->(root:Concept)
            WHERE NOT (root)-[:SUBCLASS_OF]->()
            RETURN max(length(path)) as max_depth
            """
            max_depth = await self.neo4j.run_query_value(hierarchy_query, key="max_depth")
            summary["max_hierarchy_depth"] = max_depth or 0
            
            # Connected components count
            components_query = """
            CALL gds.wcc.stats('*')
            YIELD componentCount
            RETURN componentCount
            """
            try:
                components = await self.neo4j.run_query_value(components_query, key="componentCount")
                summary["connected_components"] = components or 1
            except:
                # If GDS is not available, estimate using simpler method
                summary["connected_components"] = "N/A (requires Neo4j GDS)"
            
            logger.info("Generated ontology summary")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate ontology summary: {str(e)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to generate ontology summary: {str(e)}")
    
    async def get_concept_hierarchy(self, root_concept: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get the concept hierarchy starting from a root concept
        
        Args:
            root_concept: Name of the root concept. If None, returns all hierarchies
            
        Returns:
            List of hierarchy paths with depth information
        """
        try:
            if root_concept:
                query = """
                MATCH path = (root:Concept {name: $root_name})<-[:SUBCLASS_OF*]-(child:Concept)
                RETURN root.name as root, child.name as child, length(path) as depth
                ORDER BY depth, child.name
                """
                params = {"root_name": root_concept}
            else:
                query = """
                MATCH path = (root:Concept)<-[:SUBCLASS_OF*]-(child:Concept)
                WHERE NOT (root)-[:SUBCLASS_OF]->()
                RETURN root.name as root, child.name as child, length(path) as depth
                ORDER BY root.name, depth, child.name
                """
                params = {}
            
            result = await self.neo4j.run_query(query, params)
            logger.debug(f"Retrieved hierarchy with {len(result)} entries")
            return result
            
        except Exception as e:
            logger.error(f"Failed to get concept hierarchy: {str(e)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to get concept hierarchy: {str(e)}")
    
    async def get_node_details(
        self, 
        name: str, 
        label: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific node
        
        Args:
            name: Name of the node
            label: Optional label to filter by
            
        Returns:
            Node details including properties and relationships
        """
        try:
            # Build query based on whether label is provided
            if label:
                node_query = f"MATCH (n:{label} {{name: $name}}) RETURN n"
            else:
                node_query = "MATCH (n {name: $name}) RETURN n"
            
            # Get node details
            node_result = await self.neo4j.run_query_single(node_query, {"name": name})
            
            if not node_result:
                return None
            
            node_data = node_result.get("n", {})
            
            # Get incoming relationships
            incoming_query = """
            MATCH (other)-[r]->(n {name: $name})
            RETURN type(r) as relationship_type, other.name as other_name, 
                   labels(other) as other_labels, properties(r) as rel_properties
            """
            incoming_rels = await self.neo4j.run_query(incoming_query, {"name": name})
            
            # Get outgoing relationships
            outgoing_query = """
            MATCH (n {name: $name})-[r]->(other)
            RETURN type(r) as relationship_type, other.name as other_name,
                   labels(other) as other_labels, properties(r) as rel_properties
            """
            outgoing_rels = await self.neo4j.run_query(outgoing_query, {"name": name})
            
            details = {
                "node": node_data,
                "incoming_relationships": incoming_rels,
                "outgoing_relationships": outgoing_rels,
                "total_relationships": len(incoming_rels) + len(outgoing_rels)
            }
            
            logger.debug(f"Retrieved details for node: {name}")
            return details
            
        except Exception as e:
            logger.error(f"Failed to get node details for '{name}': {str(e)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to get node details: {str(e)}")
    
    async def delete_instance_node(
        self,
        instance_name: str,
        fail_if_not_found: bool = True
    ) -> Dict[str, Any]:
        """
        Delete an Instance node by its name and detach all of its relationships.
        Only nodes with label 'Instance' are allowed to be deleted by this method.
        
        Args:
            instance_name: Name of the Instance node to delete
            fail_if_not_found: If True, raise an error when the node does not exist
        
        Returns:
            Dictionary with write statistics (nodes_deleted, relationships_deleted, ...)
        """
        try:
            # Ensure only Instance nodes are targeted and check existence first
            existing_node = await self.get_existing_node(instance_name, label="Instance")
            if not existing_node:
                message = f"Instance '{instance_name}' not found"
                if fail_if_not_found:
                    logger.error(message)
                    raise Exception(message)
                logger.warning(message)
                return {
                    'records': [],
                    'nodes_created': 0,
                    'nodes_deleted': 0,
                    'relationships_created': 0,
                    'relationships_deleted': 0,
                    'properties_set': 0,
                    'labels_added': 0,
                    'labels_removed': 0,
                    'status': 'not_found'
                }

            # Detach and delete the instance node and all connected relationships
            delete_query = "MATCH (n:Instance {name: $name}) DETACH DELETE n"
            result = await self.neo4j.execute_write(delete_query, {"name": instance_name})
            logger.info(
                f"Deleted Instance '{instance_name}' | nodes_deleted={result.get('nodes_deleted', 0)}, "
                f"relationships_deleted={result.get('relationships_deleted', 0)}"
            )
            result['status'] = 'deleted' if result.get('nodes_deleted', 0) > 0 else 'no_op'
            return result
        except Exception as e:
            logger.error(f"Failed to delete Instance '{instance_name}': {str(e)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to delete instance node: {str(e)}")

    async def delete_nodes_by_name(
        self,
        names: List[str],
        continue_on_error: bool = True
    ) -> Dict[str, Any]:
        """
        Batch delete for Instance nodes by their names. Only deletes nodes with label 'Instance'.
        
        Args:
            names: List of Instance node names to delete
            continue_on_error: If True, continue deleting remaining names when one fails
        
        Returns:
            Aggregated deletion statistics and per-item results
        """
        aggregated = {
            'total': len(names),
            'processed': 0,
            'nodes_deleted': 0,
            'relationships_deleted': 0,
            'errors': [],
            'results': []
        }
        for name in names:
            try:
                res = await self.delete_instance_node(name, fail_if_not_found=False)
                aggregated['processed'] += 1
                aggregated['nodes_deleted'] += res.get('nodes_deleted', 0)
                aggregated['relationships_deleted'] += res.get('relationships_deleted', 0)
                aggregated['results'].append({'name': name, 'status': res.get('status', 'unknown')})
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Delete failed for Instance '{name}': {error_msg}")
                aggregated['errors'].append({'name': name, 'error': error_msg})
                if not continue_on_error:
                    break
        return aggregated

    async def delete_object_by_name(self, object_name: str, fail_if_not_found: bool = True) -> Dict[str, Any]:
        """
        Delete a specific 'Object' instance by name and all its related 'ObjectField' instances.

        - Object node: `:Instance {name: $object_name, instance_of: 'Object'}`
        - Related ObjectField nodes: `:Instance {instance_of: 'ObjectField'}` with
          relationship `[:ISOBJECTFIELDOF] -> (Object)`

        Args:
            object_name: The name of the Object instance to delete
            fail_if_not_found: If True, raise when the Object is not found

        Returns:
            Deletion stats and counts
        """
        try:
            # Check existence of the target Object instance
            exists_query = """
            MATCH (o:Instance {name: $name, instance_of: 'Object'})
            RETURN count(o) > 0 as exists
            """
            exists = await self.neo4j.run_query_value(exists_query, {"name": object_name}, key="exists")
            if not exists:
                message = f"Object '{object_name}' not found"
                if fail_if_not_found:
                    logger.error(message)
                    raise Exception(message)
                logger.warning(message)
                return {
                    'name': object_name,
                    'objects_count': 0,
                    'fields_count': 0,
                    'nodes_deleted': 0,
                    'relationships_deleted': 0,
                    'status': 'not_found'
                }

            # Pre-count related fields
            count_query = """
            MATCH (o:Instance {name: $name, instance_of: 'Object'})
            OPTIONAL MATCH (o)<-[:ISOBJECTFIELDOF]-(f:Instance {instance_of: 'ObjectField'})
            RETURN 1 as objects_count, count(DISTINCT f) as fields_count
            """
            counts = await self.neo4j.run_query_single(count_query, {"name": object_name})
            objects_count = counts.get("objects_count", 1) if counts else 1
            fields_count = counts.get("fields_count", 0) if counts else 0

            # Delete the Object and its linked ObjectFields
            delete_query = """
            MATCH (o:Instance {name: $name, instance_of: 'Object'})
            OPTIONAL MATCH (o)<-[:ISOBJECTFIELDOF]-(f:Instance {instance_of: 'ObjectField'})
            DETACH DELETE f, o
            """
            result = await self.neo4j.execute_write(delete_query, {"name": object_name})

            logger.info(
                f"Deleted Object '{object_name}' and related ObjectFields | fields={fields_count}, "
                f"nodes_deleted={result.get('nodes_deleted', 0)}, relationships_deleted={result.get('relationships_deleted', 0)}"
            )

            return {
                'name': object_name,
                'objects_count': objects_count,
                'fields_count': fields_count,
                'nodes_deleted': result.get('nodes_deleted', 0),
                'relationships_deleted': result.get('relationships_deleted', 0),
                'status': 'deleted'
            }

        except Exception as e:
            logger.error(f"Failed to delete Object '{object_name}': {str(e)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to delete Object by name: {str(e)}")

    async def search_nodes(
        self, 
        search_term: str, 
        label: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for nodes by name or properties
        
        Args:
            search_term: Term to search for
            label: Optional label to filter by
            limit: Maximum number of results
            
        Returns:
            List of matching nodes
        """
        try:
            if label:
                query = f"""
                MATCH (n:{label})
                WHERE n.name CONTAINS $search_term
                RETURN n.name as name, labels(n) as labels, properties(n) as properties
                ORDER BY n.name
                LIMIT $limit
                """
            else:
                query = """
                MATCH (n)
                WHERE n.name CONTAINS $search_term
                RETURN n.name as name, labels(n) as labels, properties(n) as properties
                ORDER BY n.name
                LIMIT $limit
                """
            
            params = {"search_term": search_term, "limit": limit}
            result = await self.neo4j.run_query(query, params)
            
            logger.debug(f"Search for '{search_term}' returned {len(result)} results")
            return result
            
        except Exception as e:
            logger.error(f"Failed to search nodes: {str(e)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to search nodes: {str(e)}")
    
    async def validate_ontology(self) -> Dict[str, Any]:
        """
        Validate the ontology for common issues
        
        Returns:
            Dictionary containing validation results and any issues found
        """
        try:
            validation_results = {
                "valid": True,
                "issues": [],
                "warnings": [],
                "statistics": {}
            }
            
            # Check for orphaned nodes (nodes with no relationships)
            orphaned_query = """
            MATCH (n)
            WHERE NOT (n)-[]-()
            RETURN count(n) as count, collect(n.name)[0..5] as sample_names
            """
            orphaned_result = await self.neo4j.run_query_single(orphaned_query)
            orphaned_count = orphaned_result.get("count", 0) if orphaned_result else 0
            
            if orphaned_count > 0:
                sample_names = orphaned_result.get("sample_names", [])
                validation_results["warnings"].append({
                    "type": "orphaned_nodes",
                    "count": orphaned_count,
                    "message": f"Found {orphaned_count} orphaned nodes",
                    "sample": sample_names
                })
            
            # Check for instances without concept relationships
            untyped_instances_query = """
            MATCH (i:Instance)
            WHERE NOT (i)-[:INSTANCE_OF]->(:Concept)
            RETURN count(i) as count, collect(i.name)[0..5] as sample_names
            """
            untyped_result = await self.neo4j.run_query_single(untyped_instances_query)
            untyped_count = untyped_result.get("count", 0) if untyped_result else 0
            
            if untyped_count > 0:
                sample_names = untyped_result.get("sample_names", [])
                validation_results["issues"].append({
                    "type": "untyped_instances",
                    "count": untyped_count,
                    "message": f"Found {untyped_count} instances without concept relationships",
                    "sample": sample_names
                })
                validation_results["valid"] = False
            
            # Check for circular subclass relationships
            circular_query = """
            MATCH path = (c:Concept)-[:SUBCLASS_OF*2..]->(c)
            RETURN count(path) as count, collect(c.name)[0..5] as sample_names
            """
            circular_result = await self.neo4j.run_query_single(circular_query)
            circular_count = circular_result.get("count", 0) if circular_result else 0
            
            if circular_count > 0:
                sample_names = circular_result.get("sample_names", [])
                validation_results["issues"].append({
                    "type": "circular_subclass",
                    "count": circular_count,
                    "message": f"Found {circular_count} circular subclass relationships",
                    "sample": sample_names
                })
                validation_results["valid"] = False
            
            # Add statistics
            validation_results["statistics"] = {
                "total_nodes": await self.get_node_count(),
                "orphaned_nodes": orphaned_count,
                "untyped_instances": untyped_count,
                "circular_references": circular_count
            }
            
            logger.info(f"Ontology validation completed. Valid: {validation_results['valid']}")
            return validation_results
            
        except Exception as e:
            logger.error(f"Failed to validate ontology: {str(e)}")
            logger.error(traceback.format_exc())
            raise Exception(f"Failed to validate ontology: {str(e)}")