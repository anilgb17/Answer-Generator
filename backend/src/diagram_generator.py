"""
Diagram Generator Module

This module provides functionality to generate visual diagrams (block diagrams,
flowcharts, hierarchy diagrams, sequence diagrams) with multi-language support.
"""

import graphviz
from typing import Dict, Any, List
from src.models import VisualElementSpec, Diagram
from src.language_service import LanguageService
from src.exceptions import DiagramGenerationError


class DiagramGenerator:
    """
    Generates visual diagrams from specifications with labels in the target language.
    
    Supports:
    - Block diagrams (component relationships)
    - Flowcharts (process flows)
    - Hierarchy diagrams (tree structures)
    - Sequence diagrams (interactions over time)
    """
    
    def __init__(self, language_service: LanguageService):
        """
        Initialize the diagram generator.
        
        Args:
            language_service: Service for language configuration
        """
        self.language_service = language_service
    
    def generate_diagram(self, spec: VisualElementSpec) -> Diagram:
        """
        Generate visual element from specification with labels in target language.
        
        Args:
            spec: Visual element specification (includes target language)
            
        Returns:
            Diagram object with image data
            
        Raises:
            DiagramGenerationError: If diagram cannot be generated
        """
        try:
            # Validate language support
            if not self.language_service.is_supported(spec.language):
                raise DiagramGenerationError(
                    f"Language '{spec.language}' is not supported for diagram generation"
                )
            
            # Get language configuration for font selection
            lang_config = self.language_service.get_language_config(spec.language)
            
            # Generate diagram based on type
            if spec.type == 'block_diagram':
                graph = self._generate_block_diagram(spec, lang_config.font_family)
            elif spec.type == 'flowchart':
                graph = self._generate_flowchart(spec, lang_config.font_family)
            elif spec.type == 'hierarchy':
                graph = self._generate_hierarchy_diagram(spec, lang_config.font_family)
            elif spec.type == 'sequence':
                graph = self._generate_sequence_diagram(spec, lang_config.font_family)
            else:
                raise DiagramGenerationError(f"Unsupported diagram type: {spec.type}")
            
            # Render to PNG
            image_data = graph.pipe(format='png')
            
            # Create caption from description
            caption = spec.description
            
            return Diagram(
                image_data=image_data,
                format='png',
                caption=caption,
                language=spec.language
            )
            
        except Exception as e:
            if isinstance(e, DiagramGenerationError):
                raise
            raise DiagramGenerationError(f"Failed to generate diagram: {str(e)}") from e
    
    def _generate_block_diagram(self, spec: VisualElementSpec, font_family: str) -> graphviz.Digraph:
        """
        Generate a block diagram showing component relationships.
        
        Args:
            spec: Visual element specification
            font_family: Font to use for labels
            
        Returns:
            Graphviz Digraph object
        """
        graph = graphviz.Digraph(comment=spec.description)
        graph.attr(rankdir='TB', fontname=font_family)
        graph.attr('node', shape='box', style='rounded,filled', fillcolor='lightblue', 
                   fontname=font_family)
        graph.attr('edge', fontname=font_family)
        
        # Add nodes
        for element in spec.elements:
            if element.get('type') == 'node':
                node_id = element.get('id', '')
                label = element.get('label', '')
                graph.node(node_id, label)
        
        # Add edges
        for element in spec.elements:
            if element.get('type') == 'edge':
                from_node = element.get('from', '')
                to_node = element.get('to', '')
                label = element.get('label', '')
                graph.edge(from_node, to_node, label=label)
        
        return graph
    
    def _generate_flowchart(self, spec: VisualElementSpec, font_family: str) -> graphviz.Digraph:
        """
        Generate a flowchart showing process flow.
        
        Args:
            spec: Visual element specification
            font_family: Font to use for labels
            
        Returns:
            Graphviz Digraph object
        """
        graph = graphviz.Digraph(comment=spec.description)
        graph.attr(rankdir='TB', fontname=font_family)
        graph.attr('node', fontname=font_family)
        graph.attr('edge', fontname=font_family)
        
        # Add nodes with different shapes based on node type
        for element in spec.elements:
            if element.get('type') == 'node':
                node_id = element.get('id', '')
                label = element.get('label', '')
                node_type = element.get('node_type', 'process')
                
                # Different shapes for different node types
                if node_type == 'start' or node_type == 'end':
                    graph.node(node_id, label, shape='ellipse', style='filled', fillcolor='lightgreen')
                elif node_type == 'decision':
                    graph.node(node_id, label, shape='diamond', style='filled', fillcolor='lightyellow')
                else:  # process
                    graph.node(node_id, label, shape='box', style='filled', fillcolor='lightblue')
        
        # Add edges
        for element in spec.elements:
            if element.get('type') == 'edge':
                from_node = element.get('from', '')
                to_node = element.get('to', '')
                label = element.get('label', '')
                graph.edge(from_node, to_node, label=label)
        
        return graph
    
    def _generate_hierarchy_diagram(self, spec: VisualElementSpec, font_family: str) -> graphviz.Digraph:
        """
        Generate a hierarchy diagram showing tree structure.
        
        Args:
            spec: Visual element specification
            font_family: Font to use for labels
            
        Returns:
            Graphviz Digraph object
        """
        graph = graphviz.Digraph(comment=spec.description)
        graph.attr(rankdir='TB', fontname=font_family)
        graph.attr('node', shape='box', style='rounded,filled', fillcolor='lightcoral',
                   fontname=font_family)
        graph.attr('edge', fontname=font_family, arrowhead='vee')
        
        # Add nodes
        for element in spec.elements:
            if element.get('type') == 'node':
                node_id = element.get('id', '')
                label = element.get('label', '')
                level = element.get('level', 0)
                
                # Different colors for different levels
                if level == 0:
                    fillcolor = 'lightcoral'
                elif level == 1:
                    fillcolor = 'lightyellow'
                else:
                    fillcolor = 'lightblue'
                
                graph.node(node_id, label, fillcolor=fillcolor)
        
        # Add edges (parent-child relationships)
        for element in spec.elements:
            if element.get('type') == 'edge':
                from_node = element.get('from', '')
                to_node = element.get('to', '')
                graph.edge(from_node, to_node)
        
        return graph
    
    def _generate_sequence_diagram(self, spec: VisualElementSpec, font_family: str) -> graphviz.Digraph:
        """
        Generate a sequence diagram showing interactions over time.
        
        Args:
            spec: Visual element specification
            font_family: Font to use for labels
            
        Returns:
            Graphviz Digraph object
        """
        graph = graphviz.Digraph(comment=spec.description)
        graph.attr(rankdir='LR', fontname=font_family)
        graph.attr('node', shape='box', style='filled', fillcolor='lightgreen',
                   fontname=font_family)
        graph.attr('edge', fontname=font_family)
        
        # Add actors/components
        for element in spec.elements:
            if element.get('type') == 'actor':
                actor_id = element.get('id', '')
                label = element.get('label', '')
                graph.node(actor_id, label)
        
        # Add interactions
        for element in spec.elements:
            if element.get('type') == 'interaction':
                from_actor = element.get('from', '')
                to_actor = element.get('to', '')
                message = element.get('message', '')
                graph.edge(from_actor, to_actor, label=message)
        
        return graph
